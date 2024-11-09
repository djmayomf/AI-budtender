import pkg_resources
import subprocess
import sys
from typing import List, Tuple, Optional
import importlib
import logging
import requests
from packaging import version
import platform
from concurrent.futures import ThreadPoolExecutor
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PackageInstaller:
    def __init__(self):
        self.installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        self.pypi_session = requests.Session()
        self.python_version = platform.python_version()
        self.os_name = platform.system().lower()
        self.architecture = platform.machine().lower()
        
    def get_package_info(self, package_name: str) -> Optional[dict]:
        """Get package information from PyPI"""
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = self.pypi_session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get info for {package_name}: {str(e)}")
            return None

    def find_compatible_version(self, package_name: str, required_version: Optional[str] = None) -> Optional[str]:
        """Find the most recent compatible version of a package"""
        try:
            package_info = self.get_package_info(package_name)
            if not package_info:
                return None

            compatible_versions = []
            for release, release_data in package_info['releases'].items():
                if not release_data:  # Skip empty releases
                    continue
                    
                # Check Python version compatibility
                python_requires = package_info['info'].get('requires_python')
                if python_requires and not self.is_python_compatible(python_requires):
                    continue

                # Check if there are wheels for this platform
                has_compatible_wheel = False
                for file_info in release_data:
                    if self.is_wheel_compatible(file_info):
                        has_compatible_wheel = True
                        break

                if has_compatible_wheel:
                    if required_version:
                        if self.versions_compatible(release, required_version):
                            compatible_versions.append(release)
                    else:
                        compatible_versions.append(release)

            if compatible_versions:
                return max(compatible_versions, key=version.parse)
            return None

        except Exception as e:
            logger.error(f"Error finding compatible version for {package_name}: {str(e)}")
            return None

    def find_alternative_package(self, package_name: str) -> Optional[str]:
        """Find alternative packages when the requested one isn't compatible"""
        try:
            # Search PyPI for similar packages
            search_url = f"https://pypi.org/search/?q={package_name}"
            response = self.pypi_session.get(search_url)
            response.raise_for_status()
            
            # Common alternative package patterns
            alternatives = {
                'pillow': ['PIL'],
                'opencv-python': ['cv2', 'opencv-python-headless'],
                'tensorflow': ['tensorflow-cpu', 'tensorflow-gpu'],
                'torch': ['pytorch', 'torch-cpu'],
                'psycopg2': ['psycopg2-binary'],
                # Add more common alternatives
            }
            
            # Check known alternatives first
            if package_name.lower() in alternatives:
                for alt in alternatives[package_name.lower()]:
                    if self.find_compatible_version(alt):
                        return alt
            
            # Try to find similar packages by name
            similar_packages = self.find_similar_packages(package_name)
            for pkg in similar_packages:
                if self.find_compatible_version(pkg):
                    return pkg
                    
            return None
            
        except Exception as e:
            logger.error(f"Error finding alternative for {package_name}: {str(e)}")
            return None

    def find_similar_packages(self, package_name: str) -> List[str]:
        """Find packages with similar names"""
        similar = []
        try:
            # Search PyPI
            search_url = f"https://pypi.org/search/?q={package_name}"
            response = self.pypi_session.get(search_url)
            response.raise_for_status()
            
            # Add common variations
            similar.extend([
                f"{package_name}-py{self.python_version.split('.')[0]}",
                f"{package_name}-{self.os_name}",
                f"{package_name}-binary",
                f"{package_name}-wheel"
            ])
            
            return similar
        except Exception:
            return []

    def is_wheel_compatible(self, file_info: dict) -> bool:
        """Check if a wheel is compatible with the current system"""
        if file_info['packagetype'] != 'bdist_wheel':
            return True  # Source distributions are always "compatible"
            
        filename = file_info['filename']
        # Check platform compatibility
        if 'any' in filename:
            return True
        if self.os_name == 'windows' and 'win' not in filename:
            return False
        if self.os_name == 'linux' and 'linux' not in filename:
            return False
        if self.os_name == 'darwin' and 'macosx' not in filename:
            return False
            
        # Check architecture compatibility
        if 'x86_64' in filename and 'x86' not in self.architecture:
            return False
            
        return True

    def versions_compatible(self, version_a: str, version_b: str) -> bool:
        """Check if two versions are compatible"""
        try:
            ver_a = version.parse(version_a)
            ver_b = version.parse(version_b)
            # Consider compatible if major versions match
            return ver_a.major == ver_b.major
        except Exception:
            return False

    def install_package_with_retry(self, package: str, max_retries: int = 3) -> bool:
        """Install package with retry logic and alternative finding"""
        package_name = package.split('==')[0].split('>=')[0].split('<=')[0].strip()
        
        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    # First try: normal installation
                    return self.install_package(package)
                elif attempt == 1:
                    # Second try: find compatible version
                    compatible_version = self.find_compatible_version(package_name)
                    if compatible_version:
                        return self.install_package(f"{package_name}=={compatible_version}")
                else:
                    # Last try: find alternative package
                    alternative = self.find_alternative_package(package_name)
                    if alternative:
                        logger.info(f"Trying alternative package: {alternative}")
                        return self.install_package(alternative)
                        
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
        return False

    def install_package(self, package: str) -> bool:
        """Install a single package"""
        try:
            logger.info(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                package,
                "--no-cache-dir"
            ])
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {str(e)}")
            return False

    def verify_installation(self, package: str) -> bool:
        """Verify if package was installed correctly"""
        package_name = package.split('==')[0].split('>=')[0].split('<=')[0]
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False

def main():
    installer = PackageInstaller()
    
    # Get missing packages
    missing_packages = installer.get_missing_packages()
    
    if not missing_packages:
        logger.info("All packages are already installed!")
        return
    
    logger.info(f"Found {len(missing_packages)} packages to install:")
    for pkg in missing_packages:
        logger.info(f"  - {pkg}")
    
    # Install missing packages with compatibility checking
    failed_packages = []
    for package in missing_packages:
        if not installer.install_package_with_retry(package):
            failed_packages.append(package)
        elif not installer.verify_installation(package):
            logger.warning(f"Package {package} installed but verification failed")
            failed_packages.append(package)
    
    # Report results
    if failed_packages:
        logger.error("\nThe following packages failed to install:")
        for pkg in failed_packages:
            logger.error(f"  - {pkg}")
    else:
        logger.info("\nAll missing packages installed successfully!")

if __name__ == "__main__":
    main()
