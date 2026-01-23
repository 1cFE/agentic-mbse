<div id="install-automator" class="section">

<span id="automator-install"></span>

# Install Automator<a href="#install-automator" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

This guide will help you install Syside Automator (available on <a href="https://pypi.org/project/syside/" class="reference external" target="_blank">PyPI</a>). It covers system requirements, installation steps, license activation, and updating.

<div id="minimum-requirements" class="section">

## Minimum Requirements<a href="#minimum-requirements" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="tab-set docutils">

<span class="nerd-font"></span> Windows

<div class="tab-content docutils">

<div class="versionadded">

<span class="versionmodified added">Added in version 0.8.4: </span>Support for Windows arm64 architecture

</div>

- System requirements:

  - Windows 10+ x64 or arm64 (for older versions, install <a href="https://www.microsoft.com/en-us/download/details.aspx?id=48234" class="reference external" target="_blank">Windows UCRT</a>)

</div>

<span class="nerd-font"></span> macOS

<div class="tab-content docutils">

- System requirements:

  - macOS Big Sur (11.0+, arm64)

  - macOS High Sierra (10.13+, x64)

</div>

<span class="nerd-font"></span> Linux

<div class="tab-content docutils">

- System requirements:

  - Linux x64 distribution with GNU C Library <span class="pre">`glibc`</span>` `<span class="pre">`>=`</span>` `<span class="pre">`2.31`</span>

  <div class="admonition note">

  Note

  Some Linux distributions like Alpine and Chimera do not include <span class="pre">`glibc`</span> and may not support running applications that require it.

  </div>

  <span class="sd-summary-icon"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1pbmZvIiBoZWlnaHQ9IjEuMGVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAxNiAxNiIgd2lkdGg9IjEuMGVtIj48cGF0aCBkPSJNMCA4YTggOCAwIDEgMSAxNiAwQTggOCAwIDAgMSAwIDhabTgtNi41YTYuNSA2LjUgMCAxIDAgMCAxMyA2LjUgNi41IDAgMCAwIDAtMTNaTTYuNSA3Ljc1QS43NS43NSAwIDAgMSA3LjI1IDdoMWEuNzUuNzUgMCAwIDEgLjc1Ljc1djIuNzVoLjI1YS43NS43NSAwIDAgMSAwIDEuNWgtMmEuNzUuNzUgMCAwIDEgMC0xLjVoLjI1di0yaC0uMjVhLjc1Ljc1IDAgMCAxLS43NS0uNzVaTTggNmExIDEgMCAxIDEgMC0yIDEgMSAwIDAgMSAwIDJaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-info" /></span><span class="sd-summary-text">How to check your glibc version</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

  <div class="sd-summary-content sd-card-body docutils">

  1.  Using gcc:

      <div class="code-wrapped highlight-shell notranslate">

      <div class="highlight">

          $(cat $(gcc -print-file-name=libc.so) | grep -P '/[^\s]+/libc\.so\.[\w]+' -o)

      </div>

      </div>

      You should see output similar to: <span class="pre">`GNU`</span>` `<span class="pre">`C`</span>` `<span class="pre">`Library`</span>` `<span class="pre">`(GNU`</span>` `<span class="pre">`libc)`</span>` `<span class="pre">`stable`</span>` `<span class="pre">`release`</span>` `<span class="pre">`version`</span>` `<span class="pre">`2.40`</span>

  2.  Using Python:

      <div class="highlight-shell notranslate">

      <div class="highlight">

          python -c "import platform; print(platform.platform())"

      </div>

      </div>

      You should see output similar to (glibc should be printed at the end): <span class="pre">`Linux-6.13.7-3-cachyos-x86_64-with-glibc2.41`</span>

  </div>

</div>

</div>

- Software requirements:

  - <a href="https://www.python.org/" class="reference external" target="_blank">Python 3.12</a> or newer

<!-- -->

- Network connectivity:

  - Internet connection is required for installation, updates and usage

<div class="admonition note">

Note

Syside Automator periodically validates license and collects basic usage data: launch time, and hashed machine ID (not personally identifiable).

Syside Automator can be used offline for short periods of time, but a fully network-isolated solution requires an offline license available on the <a href="https://sensmetry.com/syside-pricing/" class="reference external" target="_blank">Business plan</a>.

</div>

</div>

------------------------------------------------------------------------

<div id="install-python-library" class="section">

## Install Python Library<a href="#install-python-library" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

For network-isolated or air-gapped environments, see <a href="/support/offline_installation.md" class="reference internal"><span class="std std-ref">Offline Installation</span></a> page.

<div class="tab-set docutils">

Using Modeler (Recommended)

<div class="tab-content docutils">

You can install Automator automatically into a Python virtual environment using <a href="/modeler//README.md" class="reference internal"><span class="std std-ref">Modeler</span></a>. If Modeler is not installed, see <a href="/modeler/install.md" class="reference internal"><span class="std std-ref">Install Modeler</span></a> for instructions.

1.  Open Visual Studio Code or your preferred VSCodium-based editor

2.  Open your project folder (<span class="guilabel">File</span> → <span class="guilabel">Open Folder…</span>)

3.  Open any <span class="pre">`*.sysml`</span> SysML file

4.  Click on Syside logo (top right) and select <span class="guilabel">Syside Modeler: Create Python virtual environment with Syside Automator</span>

    - This command creates a virtual environment named <span class="pre">`.venv`</span> in your workspace with Automator installed.

</div>

Manual Installation

<div class="tab-content docutils">

<span class="sd-summary-text">Version History</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- **From v0.8:** Syside Automator versions 0.8 and newer are available on the official PyPI. If you wish to install older versions, use a custom index with the URL of <span class="pre">`https://gitlab.com/api/v4/projects/69960816/packages/pypi/simple`</span>

</div>

Syside Automator is available on <a href="https://pypi.org/project/syside/" class="reference external" target="_blank">Python Package Index (PyPI)</a>. You can install it using any preferred Python package manager, such as <span class="pre">`pip`</span>:

1.  Open a terminal and create a Python virtual environment

    <div class="code-wrapped highlight-bash notranslate">

    <div class="highlight">

        python -m venv .venv

    </div>

    </div>

2.  Activate the created virtual environment (see <a href="/support/offline_installation.md" class="reference internal"><span class="std std-ref">How to manually activate virtual environment</span></a>)

3.  Run the following command:

    <div class="code-wrapped highlight-bash notranslate">

    <div class="highlight">

        pip install syside

    </div>

    </div>

    You should see output similar to: <span class="pre">`Successfully`</span>` `<span class="pre">`installed`</span>` `<span class="pre">`syside-x.x.x`</span>

</div>

</div>

Before running Python scripts that use Syside Automator, ensure that virtual environment is activated.

<span class="sd-summary-icon"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1pbmZvIiBoZWlnaHQ9IjEuMGVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAxNiAxNiIgd2lkdGg9IjEuMGVtIj48cGF0aCBkPSJNMCA4YTggOCAwIDEgMSAxNiAwQTggOCAwIDAgMSAwIDhabTgtNi41YTYuNSA2LjUgMCAxIDAgMCAxMyA2LjUgNi41IDAgMCAwIDAtMTNaTTYuNSA3Ljc1QS43NS43NSAwIDAgMSA3LjI1IDdoMWEuNzUuNzUgMCAwIDEgLjc1Ljc1djIuNzVoLjI1YS43NS43NSAwIDAgMSAwIDEuNWgtMmEuNzUuNzUgMCAwIDEgMC0xLjVoLjI1di0yaC0uMjVhLjc1Ljc1IDAgMCAxLS43NS0uNzVaTTggNmExIDEgMCAxIDEgMC0yIDEgMSAwIDAgMSAwIDJaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-info" /></span><span class="sd-summary-text">How to manually activate virtual environment</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

<div class="tab-set docutils">

<span class="nerd-font"></span> Windows

<div class="tab-content docutils">

1.  Run the following command in the terminal:

    1.  Using Command Prompt:

        <div class="code-wrapped highlight-shell notranslate">

        <div class="highlight">

            .\.venv\Scripts\activate

        </div>

        </div>

    2.  Using PowerShell:

        <div class="code-wrapped highlight-pwsh notranslate">

        <div class="highlight">

            .\.venv\Scripts\Activate.ps1

        </div>

        </div>

        PowerShell may block the activation with a “scripts disabled” error. Run the following command to allow script execution:

        <div class="code-wrapped highlight-pwsh notranslate">

        <div class="highlight">

            Set-ExecutionPolicy Bypass -Scope Process -Force

        </div>

        </div>

2.  Run the following command to verify that the virtual environment was successfully activated:

    <div class="code-wrapped highlight-bash notranslate">

    <div class="highlight">

        where.exe python

    </div>

    </div>

    The printed path should end with: <span class="pre">`/.venv/bin/python`</span>

</div>

<span class="nerd-font"></span> macOS / <span class="nerd-font"></span> Linux

<div class="tab-content docutils">

1.  Run the following command in the terminal:

    <div class="code-wrapped highlight-bash notranslate">

    <div class="highlight">

        source .venv/bin/activate

    </div>

    </div>

2.  Run the following command to verify that the virtual environment was successfully activated:

    <div class="code-wrapped highlight-bash notranslate">

    <div class="highlight">

        which python

    </div>

    </div>

    The printed path should end with: <span class="pre">`/.venv/bin/python`</span>

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div id="activate-license" class="section">

<span id="automator-license-activation"></span>

## Activate License<a href="#activate-license" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<span class="sd-summary-text">Version History</span><span class="sd-summary-state-marker sd-summary-chevron-right"><img src="data:image/svg+xml;base64,PHN2ZyBhcmlhLWhpZGRlbj0idHJ1ZSIgY2xhc3M9InNkLW9jdGljb24gc2Qtb2N0aWNvbi1jaGV2cm9uLXJpZ2h0IiBoZWlnaHQ9IjEuNWVtIiB2ZXJzaW9uPSIxLjEiIHZpZXdib3g9IjAgMCAyNCAyNCIgd2lkdGg9IjEuNWVtIj48cGF0aCBkPSJNOC43MiAxOC43OGEuNzUuNzUgMCAwIDEgMC0xLjA2TDE0LjQ0IDEyIDguNzIgNi4yOGEuNzUxLjc1MSAwIDAgMSAuMDE4LTEuMDQyLjc1MS43NTEgMCAwIDEgMS4wNDItLjAxOGw2LjI1IDYuMjVhLjc1Ljc1IDAgMCAxIDAgMS4wNmwtNi4yNSA2LjI1YS43NS43NSAwIDAgMS0xLjA2IDBaIiAvPjwvc3ZnPg==" class="sd-octicon sd-octicon-chevron-right" /></span>

<div class="sd-summary-content sd-card-body docutils">

- **From v0.8:** License activation process was simplified. The <span class="pre">`syside-license`</span> package is now only required for network-isolated or air-gapped environments (see <a href="/support/offline_installation.md" class="reference internal"><span class="std std-ref">Offline Installation</span></a> page).

</div>

<div class="admonition warning">

Warning

License keys are sensitive information, keep them private and secure. Exposure may result in unauthorized use or license revocation.

</div>

Syside Automator automatically validates the license each time <span class="pre">`import`</span>` `<span class="pre">`syside`</span> is called. Syside Automator expects the license key to be stored in one of the following locations:

<div class="tab-set docutils">

.env file

<div class="tab-content docutils">

For local development, you can store the license key in a <span class="pre">`.env`</span> file:

1.  Create a new file named <span class="pre">`.env`</span> in the root of your project directory

2.  Add your license key to the file:

    <div class="highlight-text notranslate">

    <div class="highlight">

        SYSIDE_LICENSE_KEY=<your-license-key>

    </div>

    </div>

<div class="admonition tip">

Tip

If you are using <span class="pre">`git`</span> for version control, make sure to add <span class="pre">`.env`</span> to your <span class="pre">`.gitignore`</span> file and never commit the <span class="pre">`.env`</span> file to your repository.

For GitLab users, you can also use repository-wide push rules to prevent uploading secrets. See <a href="https://docs.gitlab.com/user/project/repository/push_rules/#prohibit-files-by-name" class="reference external" target="_blank">GitLab documentation</a> for details.

</div>

</div>

Environment variable

<div class="tab-content docutils">

Set the <span class="pre">`SYSIDE_LICENSE_KEY`</span> environment variable by running the following command:

1.  Windows (PowerShell):

    <div class="code-wrapped highlight-pwsh notranslate">

    <div class="highlight">

        $env:SYSIDE_LICENSE_KEY = "<your-license-key>"

    </div>

    </div>

2.  macOS / Linux (terminal):

    <div class="code-wrapped highlight-bash notranslate">

    <div class="highlight">

        export SYSIDE_LICENSE_KEY=<your-license-key>

    </div>

    </div>

</div>

Secret Storage (Keyring)

<div class="tab-content docutils">

Store your license key in the Operating System’s secret storage:

- Windows: Windows Credential Store

- macOS: Keychain credential store

- Linux: depends on your desktop environment (KDE Wallet on Kubuntu, Passwords and Keys on Ubuntu)

<div class="admonition note">

Note

Storing in the secret storage is not supported on systems without the desktop environment such as Docker containers and WSL.

</div>

Using the secret storage keeps the key secure and available across all your Python projects without storing it in code or configuration files.

1.  Using Modeler (Recommended):

    1.  Open Visual Studio Code or your preferred VSCodium-based editor

    2.  Open the Command Palette <span class="kbd kbd compound docutils literal notranslate"><span class="kbd kbd docutils literal notranslate">Ctrl/Cmd</span>-<span class="kbd kbd docutils literal notranslate">Shift</span>-<span class="kbd kbd docutils literal notranslate">P</span></span>

    3.  Type <span class="guilabel">Syside Modeler: Add Syside license key to keyring</span>

        - If you’ve already activated a license in Modeler, it will be stored automatically

        - Otherwise, you’ll be prompted to enter your license key

2.  Using Python’s <a href="https://pypi.org/project/keyring/" class="reference external" target="_blank">keyring library</a>

    <div class="code-wrapped highlight-bash notranslate">

    <div class="highlight">

        >>> import keyring
        >>> keyring.set_password("license-key.syside", "license-key", "<your-license-key>")

    </div>

    </div>

Once stored, <span class="pre">`import`</span>` `<span class="pre">`syside`</span> will automatically retrieve the license from your keyring in any Python environment. No additional configuration needed.

**Scope:** The license key is stored per-user and works across all virtual environments and projects on your machine. Other users on the same computer will need to store their own license keys.

</div>

</div>

------------------------------------------------------------------------

<div id="activate-license-in-ci-cd" class="section">

### Activate License in CI/CD<a href="#activate-license-in-ci-cd" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

<div class="admonition note">

Note

Using Automator in CI/CD requires a Deployment License Key (available under the <a href="https://sensmetry.com/syside-pricing/" class="reference external" target="_blank">Business plan</a>).

The deployment license key starts with <span class="pre">`CI-`</span> to make it easier to distinguish.

</div>

Most CI/CD providers have secure secret storage for environment variables. Use your provider’s secret management instead of <span class="pre">`.env`</span> files to store your deployment key as <span class="pre">`SYSIDE_LICENSE_KEY`</span>.

<div class="tab-set docutils">

<span class="nerd-font"></span> GitLab

<div class="tab-content docutils">

Add <span class="pre">`SYSIDE_LICENSE_KEY`</span> as a masked CI/CD variable in your project settings (see <a href="https://docs.gitlab.com/ci/variables/#define-a-cicd-variable-in-the-ui" class="reference external" target="_blank">GitLab CI/CD variables documentation</a>).

</div>

<span class="nerd-font"></span> GitHub

<div class="tab-content docutils">

Add <span class="pre">`SYSIDE_LICENSE_KEY`</span> as a repository secret in your repository settings (see <a href="https://docs.github.com/en/actions/reference/encrypted-secrets" class="reference external" target="_blank">GitHub secrets documentation</a>).

</div>

</div>

</div>

</div>

------------------------------------------------------------------------

<div id="verify-installation" class="section">

## Verify Installation<a href="#verify-installation" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Once Syside Automator is installed and activated, follow these steps to quickly verify it is working as expected.

1.  Open a terminal in your project folder

2.  Activate the virtual environment with Syside Automator installed (see <a href="/support/offline_installation.md" class="reference internal"><span class="std std-ref">How to manually activate virtual environment</span></a>)

3.  Start a Python shell and execute <span class="pre">`import`</span>` `<span class="pre">`syside`</span>:

    <div class="code-wrapped highlight-bash notranslate">

    <div class="highlight">

        python -c "import syside; print(syside.__version__)"

    </div>

    </div>

If the import succeeds without errors, Syside Automator version will be displayed: <span class="pre">`x.x.x`</span>.

<div class="admonition note">

Note

If you get <span class="pre">`ModuleNotFoundError:`</span>` `<span class="pre">`No`</span>` `<span class="pre">`module`</span>` `<span class="pre">`named`</span>` `<span class="pre">`'syside'`</span>, ensure you activated the correct virtual environment where Syside was installed.

</div>

</div>

------------------------------------------------------------------------

<div id="update-automator" class="section">

## Update Automator<a href="#update-automator" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

You can update Automator using any preferred Python package manager, such as <span class="pre">`pip`</span>:

1.  Open a terminal

2.  Activate the virtual environment with Syside Automator installed (see <a href="/support/offline_installation.md" class="reference internal"><span class="std std-ref">How to manually activate virtual environment</span></a>)

3.  Run the following command:

    <div class="code-wrapped highlight-bash notranslate">

    <div class="highlight">

        pip install syside --upgrade

    </div>

    </div>

</div>

------------------------------------------------------------------------

<div id="what-s-next" class="section">

## What’s Next?<a href="#what-s-next" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

With Syside Automator is installed and working, continue to the following pages to learn more:

- Check out the <a href="/automator/essentials.md" class="reference internal"><span class="std std-ref">Essentials</span></a> section to learn about available features

- Learn with <a href="/automator/first_example.md" class="reference internal"><span class="std std-ref">First Example</span></a> to build your first script

- Explore the <a href="/examples//README.md" class="reference internal"><span class="std std-ref">Examples Collection</span></a> to see practical use cases and code samples

- Check out the <a href="/python/v0.8.4//README.md" class="reference external">API Reference</a> for complete API documentation

</div>

</div>
