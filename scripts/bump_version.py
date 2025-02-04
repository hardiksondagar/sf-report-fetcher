import re
import sys
from pathlib import Path

def bump_version(version_type='patch'):
    """
    Bump the version number in version.py
    version_type can be 'major', 'minor', or 'patch'
    """
    version_file = Path('salesforce_report_fetcher/version.py')
    content = version_file.read_text()
    
    # Extract current version
    match = re.search(r'VERSION = "(\d+)\.(\d+)\.(\d+)"', content)
    if not match:
        print("Could not find version string")
        return
    
    major, minor, patch = map(int, match.groups())
    
    # Update version based on type
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f'{major}.{minor}.{patch}'
    new_content = re.sub(
        r'VERSION = "\d+\.\d+\.\d+"',
        f'VERSION = "{new_version}"',
        content
    )
    
    # Write new version
    version_file.write_text(new_content)
    print(f"Version bumped to {new_version}")
    return new_version

if __name__ == '__main__':
    version_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    bump_version(version_type)