"""
GitHub integration for run-git
Handles repo creation, authentication, and GitHub API operations
"""
import os
import yaml
import requests
from pathlib import Path
from github import Github, GithubException
import questionary
from gitpush.ui.banner import show_success, show_error, show_warning, show_info, show_progress


class GitHubManager:
    """Manage GitHub operations"""
    
    CONFIG_DIR = Path.home() / '.run-git'
    CONFIG_FILE = CONFIG_DIR / 'config.yml'
    
    def __init__(self):
        self.token = None
        self.github = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    config = yaml.safe_load(f)
                    self.token = config.get('github_token')
                    if self.token:
                        self.github = Github(self.token)
        except Exception as e:
            show_warning(f"Could not load config: {str(e)}")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            self.CONFIG_DIR.mkdir(exist_ok=True)
            config = {'github_token': self.token}
            with open(self.CONFIG_FILE, 'w') as f:
                yaml.dump(config, f)
            # Set file permissions to user-only
            os.chmod(self.CONFIG_FILE, 0o600)
            show_success("GitHub token saved securely")
        except Exception as e:
            show_error(f"Failed to save config: {str(e)}")
    
    def authenticate(self):
        """Authenticate with GitHub"""
        if self.token and self.github:
            # Verify existing token
            try:
                self.github.get_user().login
                return True
            except:
                show_warning("Saved token is invalid")
                self.token = None
        
        # Get new token
        show_info("\nGitHub Personal Access Token needed!")
        show_info("Create one at: https://github.com/settings/tokens")
        show_info("Required scopes: repo, user")
        
        token = questionary.password("Enter your GitHub token:").ask()
        
        if not token:
            show_error("Token is required")
            return False
        
        # Validate token
        try:
            gh = Github(token)
            user = gh.get_user().login
            show_success(f"Authenticated as: {user}")
            self.token = token
            self.github = gh
            self._save_config()
            return True
        except Exception as e:
            show_error(f"Authentication failed: {str(e)}")
            return False
    
    def get_gitignore_templates(self):
        """Get list of popular gitignore templates"""
        popular = [
            'Python', 'Node', 'Java', 'Go', 'Rust', 'C++', 'C', 
            'Ruby', 'PHP', 'Swift', 'Kotlin', 'Dart', 'R',
            'VisualStudio', 'JetBrains', 'Vim', 'Emacs', 'macOS', 'Windows', 'Linux'
        ]
        return popular
    
    def get_license_templates(self):
        """Get list of common licenses"""
        return {
            'MIT': 'mit',
            'Apache 2.0': 'apache-2.0',
            'GPL v3': 'gpl-3.0',
            'BSD 3-Clause': 'bsd-3-clause',
            'ISC': 'isc',
            'None': None
        }
    
    def repo_exists(self, repo_name):
        """Check if repository already exists"""
        try:
            user = self.github.get_user()
            user.get_repo(repo_name)
            return True
        except:
            return False
    
    def suggest_repo_name(self, base_name):
        """Suggest alternative repo name if exists"""
        counter = 1
        while True:
            new_name = f"{base_name}-{counter}"
            if not self.repo_exists(new_name):
                return new_name
            counter += 1
            if counter > 10:
                # Fallback to timestamp
                import time
                return f"{base_name}-{int(time.time())}"
    
    def detect_language(self):
        """Auto-detect language from current directory"""
        # Check for common files
        if Path('requirements.txt').exists() or Path('setup.py').exists():
            return 'Python'
        elif Path('package.json').exists():
            return 'Node'
        elif Path('pom.xml').exists() or Path('build.gradle').exists():
            return 'Java'
        elif Path('go.mod').exists():
            return 'Go'
        elif Path('Cargo.toml').exists():
            return 'Rust'
        elif Path('Gemfile').exists():
            return 'Ruby'
        elif Path('composer.json').exists():
            return 'PHP'
        return 'Python'  # Default
    
    def create_repository(self, config):
        """Create repository on GitHub"""
        try:
            user = self.github.get_user()
            
            # Create repo
            show_progress(f"Creating repository '{config['name']}' on GitHub...")
            
            repo = user.create_repo(
                name=config['name'],
                description=config.get('description', ''),
                private=config.get('private', False),
                auto_init=False,  # We'll init locally
                gitignore_template=config.get('gitignore'),
                license_template=config.get('license')
            )
            
            show_success(f"Repository created: {repo.html_url}")
            return repo
            
        except GithubException as e:
            if e.status == 422:
                show_error(f"Repository '{config['name']}' already exists!")
                suggestion = self.suggest_repo_name(config['name'])
                show_info(f"Suggested name: {suggestion}")
                
                use_suggestion = questionary.confirm(
                    f"Use '{suggestion}' instead?"
                ).ask()
                
                if use_suggestion:
                    config['name'] = suggestion
                    return self.create_repository(config)
            else:
                show_error(f"Failed to create repository: {str(e)}")
            return None
        except Exception as e:
            show_error(f"Error: {str(e)}")
            return None
    
    def get_gitignore_content(self, template):
        """Get gitignore content from GitHub API"""
        try:
            url = f"https://api.github.com/gitignore/templates/{template}"
            headers = {'Authorization': f'token {self.token}'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('source', '')
            return None
        except:
            return None
    
    def get_license_content(self, license_key, author_name):
        """Get license content from GitHub API"""
        try:
            url = f"https://api.github.com/licenses/{license_key}"
            response = requests.get(url)
            if response.status_code == 200:
                content = response.json().get('body', '')
                # Replace placeholders
                import datetime
                year = datetime.datetime.now().year
                content = content.replace('[year]', str(year))
                content = content.replace('[fullname]', author_name)
                return content
            return None
        except:
            return None
