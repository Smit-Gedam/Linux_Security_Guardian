/*
 UNIX domain socket rule engine server.
 Listens on /tmp/guardian_rules.sock
 Protocol: client sends a single line: TYPE|DETAILS

 Server responds with a single byte severity '0','1','2' and newline.
*/

#include <sys/socket.h>
#include <sys/un.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define SOCKET_PATH "/tmp/guardian_rules.sock"
#define BUF_SIZE 8192

int evaluate(const char *type, const char *details) {
    if (strcmp(type, "FILE_MOD") == 0) {
        if (strstr(details, "/bin") || strstr(details, "/sbin") || strstr(details, "/etc")) return 2;
        return 1;
    }
    if (strcmp(type, "PROCESS") == 0) {
        if (strstr(details, "/tmp") || strchr(details, '?')) return 1;
        return 0;
    }
    if (strcmp(type, "NETWORK") == 0) {
        if (strstr(details, "198.51.100.") || strstr(details, "203.0.113.")) return 2;
        return 0;
    }
    if (strcmp(type, "LOGIN_FAIL") == 0) {
        int failures = atoi(details);
        if (failures >= 5) return 2;
        if (failures >= 3) return 1;
        return 0;
    }
    return 0;
}

int main() {
    int server_fd, client_fd;
    struct sockaddr_un addr;
    char buf[BUF_SIZE];

    unlink(SOCKET_PATH);
    server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); exit(1); }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path)-1);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        perror("bind"); exit(1);
    }

    if (listen(server_fd, 5) == -1) { perror("listen"); exit(1); }

    printf("Rule engine server listening on %s", SOCKET_PATH);
    while (1) {
        client_fd = accept(server_fd, NULL, NULL);
        if (client_fd == -1) { perror("accept"); continue; }
        ssize_t r = read(client_fd, buf, BUF_SIZE-1);
        if (r > 0) {
            buf[r] = ' ';
            // parse
            char *sep = strchr(buf, '|');
            if (!sep) {
                write(client_fd, "0", 2);
                close(client_fd); continue;
            }
            *sep = ' ';
            char *type = buf;
            char *details = sep + 1;
            // strip newline
            char *nl = strchr(details, '\n'); if (nl) *nl=' ';
            int sev = evaluate(type, details);
            char out[4]; snprintf(out, sizeof(out), "%d", sev);
            write(client_fd, out, strlen(out));
        }
        close(client_fd);
    }
    close(server_fd);
    unlink(SOCKET_PATH);
    return 0;
}
