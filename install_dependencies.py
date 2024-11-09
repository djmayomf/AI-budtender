import subprocess
import sys
import os

def install_package(package):
    """Install a package with pip and handle errors"""
    try:
        # First attempt: normal installation
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        try:
            # Second attempt: force reinstall
            print(f"Retrying {package} with force reinstall...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--force-reinstall", "--no-cache-dir", package
            ])
        except subprocess.CalledProcessError:
            try:
                # Third attempt: with --user flag
                print(f"Retrying {package} with user installation...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "--user", package
                ])
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {package}: {str(e)}")
                return False
    return True

def setup_virtual_env():
    """Create and activate virtual environment"""
    try:
        # Create venv if it doesn't exist
        if not os.path.exists('venv'):
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        
        # Activate venv
        if sys.platform == 'win32':
            activate_script = os.path.join('venv', 'Scripts', 'activate.bat')
        else:
            activate_script = os.path.join('venv', 'bin', 'activate')
        
        subprocess.check_call(activate_script, shell=True)
        return True
    except Exception as e:
        print(f"Failed to setup virtual environment: {str(e)}")
        return False

def upgrade_pip():
    """Upgrade pip to latest version"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to upgrade pip: {str(e)}")
        return False

def install_requirements():
    """Install all requirements with error handling"""
    # Required packages for the installation
    base_packages = [
        'wheel',
        'setuptools',
        'pip-tools'
    ]
    
    # Install base packages first
    for package in base_packages:
        if not install_package(package):
            print(f"Failed to install base package: {package}")
            return False

    # Read requirements file
    try:
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print("requirements.txt not found!")
        return False

    # Install each requirement
    failed_packages = []
    for req in requirements:
        if not install_package(req):
            failed_packages.append(req)

    if failed_packages:
        print("\nFailed to install the following packages:")
        for package in failed_packages:
            print(f"- {package}")
        return False
    
    return True

def main():
    """Main installation process"""
    print("Starting installation process...")
    
    # Setup virtual environment
    if not setup_virtual_env():
        print("Failed to setup virtual environment")
        return
    
    # Upgrade pip
    if not upgrade_pip():
        print("Failed to upgrade pip")
        return
    
    # Install requirements
    if install_requirements():
        print("\nAll packages installed successfully!")
    else:
        print("\nSome packages failed to install. Please check the output above.")

if __name__ == "__main__":
    main()
