#!/bin/bash

# Exit on any error
set -e

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}📝 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a Git repository!"
    exit 1
fi

# Get current branch and check if we're on main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "You're currently on '$CURRENT_BRANCH' branch, not 'main'"
    read -p "Do you want to switch to main branch? (yes/no): " SWITCH_MAIN
    if [[ "$SWITCH_MAIN" == "yes" || "$SWITCH_MAIN" == "y" ]]; then
        git checkout main
        CURRENT_BRANCH="main"
    else
        print_warning "Continuing with current branch: $CURRENT_BRANCH"
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_status "Current changes:"
    git status --short
    
    read -p "Stage all changes for commit? (yes/no/skip): " STAGE_ANSWER
    case $STAGE_ANSWER in
        yes|y)
            git add -A
            print_success "All changes staged"
            ;;
        no|n)
            print_status "Please stage files manually with 'git add <files>' then press Enter"
            read
            ;;
        skip|s)
            print_warning "Skipping - no changes will be committed"
            ;;
        *)
            print_error "Invalid choice. Exiting."
            exit 1
            ;;
    esac
else
    print_warning "No changes to commit!"
    exit 0
fi

# Ask for commit message
while true; do
    read -p "📝 Describe your changes: " COMMIT_MSG
    if [ -n "$COMMIT_MSG" ]; then
        break
    else
        print_error "Commit message cannot be empty."
    fi
done

# Create timestamped branch
VERSION_NAME="version-$(date +'%Y.%m.%d-at-%H.%M.%S')"
print_status "Creating new branch: $VERSION_NAME"

# Update main branch
git pull origin main

# Create and switch to new branch
git checkout -b "$VERSION_NAME"

# Commit changes
git commit -m "$COMMIT_MSG"
print_success "Changes committed to branch $VERSION_NAME"

# Push branch
git push -u origin "$VERSION_NAME"
print_success "Branch $VERSION_NAME pushed to remote"

# Ask for merge
read -p "Merge this branch into main? (yes/no): " MERGE_ANSWER
if [[ "$MERGE_ANSWER" != "yes" && "$MERGE_ANSWER" != "y" ]]; then
    print_success "Branch created and pushed. No merge performed."
    echo "Branch: $VERSION_NAME"
    echo "Commit: $COMMIT_MSG"
    exit 0
fi

# Attempt merge with merge commit
print_status "Attempting to merge $VERSION_NAME into main..."
git checkout main
git pull origin main

# Check if we can fast-forward
if git merge --ff-only "$VERSION_NAME" 2>/dev/null; then
    print_success "Fast-forward merge completed"
else
    # Non-fast-forward merge
    print_status "Performing merge commit..."
    if git merge --no-ff "$VERSION_NAME" -m "Merge $VERSION_NAME: $COMMIT_MSG"; then
        print_success "Merge completed successfully"
    else
        # Handle conflicts
        print_warning "Merge conflicts detected!"
        
        CONFLICTS=$(git diff --name-only --diff-filter=U)
        echo "Conflicts in:"
        echo "$CONFLICTS"
        
        echo -e "\nOptions:"
        echo "1) Resolve conflicts manually"
        echo "2) Use 'main' version for all conflicts"
        echo "3) Use 'branch' version for all conflicts" 
        echo "4) Abort merge"
        
        read -p "Choose option (1-4): " RESOLVE_OPTION
        
        case $RESOLVE_OPTION in
            1)
                print_status "Please resolve conflicts manually and then press Enter to continue..."
                read
                git add -A
                git commit -m "Resolved merge conflicts: $COMMIT_MSG"
                print_success "Conflicts resolved manually"
                ;;
            2)
                for file in $CONFLICTS; do
                    git checkout --ours "$file"
                    git add "$file"
                done
                git commit -m "Resolved conflicts using main version: $COMMIT_MSG"
                print_success "Used main version for all conflicts"
                ;;
            3)
                for file in $CONFLICTS; do
                    git checkout --theirs "$file"
                    git add "$file"
                done
                git commit -m "Resolved conflicts using branch version: $COMMIT_MSG"
                print_success "Used branch version for all conflicts"
                ;;
            4)
                git merge --abort
                print_warning "Merge aborted. Branch $VERSION_NAME was created but not merged."
                exit 0
                ;;
            *)
                print_error "Invalid option. Aborting merge."
                git merge --abort
                exit 1
                ;;
        esac
    fi
fi

# Push main after successful merge
print_status "Pushing main branch..."
git push origin main
print_success "Main branch updated successfully!"

# Cleanup
read -p "Delete the feature branch $VERSION_NAME? (yes/no): " DELETE_BRANCH
if [[ "$DELETE_BRANCH" == "yes" || "$DELETE_BRANCH" == "y" ]]; then
    git branch -d "$VERSION_NAME"
    print_success "Branch $VERSION_NAME deleted locally"
    
    read -p "Also delete from remote? (yes/no): " DELETE_REMOTE
    if [[ "$DELETE_REMOTE" == "yes" || "$DELETE_REMOTE" == "y" ]]; then
        git push origin --delete "$VERSION_NAME"
        print_success "Branch $VERSION_NAME deleted from remote"
    fi
fi

print_success "All operations completed successfully! 🎉"
