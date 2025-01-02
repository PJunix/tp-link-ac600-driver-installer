import subprocess
import requests

def install_package(package_name):
    """Check if a package is installed, and install it if it is not."""
    try:
        subprocess.run(["dpkg", "-s", package_name], check=True)
    except subprocess.CalledProcessError:
        print(f"Installing {package_name}...")
        subprocess.run(["sudo", "apt-get", "install", "-y", package_name], check=True)

def install_bc_if_missing():
    """Ensure that 'bc' is installed, required for some operations."""
    try:
        subprocess.run(["dpkg", "-s", "bc"], check=True)
    except subprocess.CalledProcessError:
        install_package("bc")

def get_kernel_version():
    """Retrieve the kernel version using uname."""
    try:
        kernel_version = subprocess.run(
            ["uname", "-r"], capture_output=True, text=True, check=True
        ).stdout.strip()
        return kernel_version
    except subprocess.CalledProcessError as e:
        print(f"Error fetching kernel version: {e}")
        return None

def get_available_kernel_packages(kernel_version):
    """Query apt-cache for available kernel packages for the given kernel version."""
    try:
        result = subprocess.run(
            ["apt-cache", "search", f"linux-headers-{kernel_version}"],
            capture_output=True, text=True, check=True
        )
        # Parse the output to get the package names for headers and kbuild
        packages = []
        for line in result.stdout.split("\n"):
            if f"{kernel_version}" in line:
                packages.append(line.split()[0])
        return packages
    except subprocess.CalledProcessError as e:
        print(f"Error querying available kernel packages: {e}")
        return []

def generate_urls(kernel_version, packages):
    """Generate download URLs based on the kernel version and available packages."""
    base_url = "https://kali.download/kali/pool/main/l/linux/"
    urls = [base_url + package for package in packages]
    return urls

def url_exists(url):
    """Check if the URL exists."""
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        print(f"Error checking URL: {url}")
        return False

def download_package(url):
    """Download the package from the given URL."""
    file_name = url.split('/')[-1]
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {file_name}")
        return file_name
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return None

def install_downloaded_package(file_name):
    """Install the downloaded package."""
    try:
        subprocess.run(["sudo", "dpkg", "-i", file_name], check=True)
        print(f"Installed {file_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {file_name}: {e}")
        print("Attempting to fix broken dependencies...")
        subprocess.run(["sudo", "apt-get", "install", "-f"], check=True)

def print_colored_message(kernel_version):
    """Print a colorful message notifying the kernel version and package compatibility."""
    package_version = "6.11.2"  # This is the version we aim to match for the AC600

    # ANSI escape codes for colors
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Colorful and bold message
    print(f"{RED}{BOLD}Your kernel version is: {RESET}{kernel_version}")
    print(f"{YELLOW}{BOLD}Attempting to find matching packages for kernel version: {RESET}{package_version}")
    print(f"{BLUE}{BOLD}Proceeding with package search and installation...{RESET}")

def clone_and_install_driver(repo_url):
    """Clone the git repository and run the install-driver.sh script."""
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    try:
        subprocess.run(["git", "clone", repo_url], check=True)
        print(f"Cloned repository {repo_name}")
        subprocess.run(["sudo", "chmod", "+x", "install-driver.sh"], cwd=repo_name, check=True)

        # Ensure kernel headers are installed
        install_package(f"linux-headers-{get_kernel_version()}")

        # Run the install-driver.sh script
        subprocess.run(["sudo", "./install-driver.sh"], cwd=repo_name, check=True)
        print("Driver installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install driver from {repo_name}: {e}")

def main():
    # Ensure 'bc' is installed if missing
    install_bc_if_missing()

    kernel_version = get_kernel_version()
    if not kernel_version:
        print("Failed to retrieve kernel version. Exiting...")
        return

    print_colored_message(kernel_version)

    # Get the available kernel packages for the detected kernel version
    packages = get_available_kernel_packages(kernel_version)
    if not packages:
        print(f"No packages found for kernel version {kernel_version}. Exiting...")
        return

    # Generate download URLs for the packages
    urls = generate_urls(kernel_version, packages)

    # Attempt to download and install the packages
    for url in urls:
        if url_exists(url):
            file_name = download_package(url)
            if file_name:
                install_downloaded_package(file_name)
        else:
            print(f"URL does not exist: {url}")

    # Clone the specified repository and run the install-driver.sh script
    repo_url = "https://github.com/morrownr/8821au-20210708.git"
    clone_and_install_driver(repo_url)

if __name__ == "__main__":
    main()
