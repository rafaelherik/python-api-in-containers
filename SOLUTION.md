## ABN Technical assesment solution implementation

### First impressions

When running the API's I've experienced an incompatibility between pytorch cpu only libraris with Apple M3 processor.

I've checked the official documentation and I could not find the specific **torch**+cpu ([PyTorch](https://pytorch.org)) packages for ARM architecture. Then I've used a **GPU** package with the same version to run the API's locally. I've tested in and64 VM and the +CPU packages are running fine. I will continue the solution using the GPU packages.

When installing the +cpu package it could not be found on the public index, then I've used the Pytorch repository to download the specific versions(https://download.pytorch.org/whl/cpu).

To run the backend API I've added two new files to be easier to manage multiple indexes dependencies, as it's not recommended to add the "--extra-index-urls" to prevent malicious code from packages on public source with the same name and version of packages on private soruce, I've spllited thre requirements in two files, and the script will help to manage the installation:

- build.sh - Install dependencies from multiple sources.

- run.sh - Install dependencies and start the API.

To run locally I've used Python3.10 due some dependencies limitations.

### New Backend API