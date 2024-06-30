## ABN Technical assesment solution implementation

## First impressions

When running the API's I've experienced an incompatibility between pytorch cpu only libraris with Apple M3 processor.

I've checked the official documentation and I could not find the specific **torch**+cpu ([PyTorch](https://pytorch.org)) packages for ARM architecture. Then I've used a **GPU** package with the same version to run the API's locally. I've tested in and64 VM and the +CPU packages are running fine. I will continue the solution using the GPU packages.

When installing the +cpu package it could not be found on the public index, then I've used the Pytorch repository to download the specific versions(https://download.pytorch.org/whl/cpu).

To run the backend API I've added two new files to be easier to manage multiple indexes dependencies, as it's not recommended to add the "--extra-index-urls" to prevent malicious code from packages on public source with the same name and version of packages on private soruce, I've spllited thre requirements in two files, and the script will help to manage the installation:

- build.sh - Install dependencies from multiple sources.

- run.sh - Install dependencies and start the API.

To run locally I've used Python3.10 due some dependencies limitations.

## New Backend API

### EXTERNAL_INTEGRATION_KEY

I've changed a small typo on the EXTERNAL_INTEGRATION_KEY - It was EXTERNAL_INTGERATION_KEY before.

I've added the environment variable dependency, and also the FLESK_ENV variable dependency, to diferentiate the environment that the application is running:

```python
if __name__ == '__main__':
    mode = os.getenv('FLASK_ENV', 'production')    
    debug = mode == 'development'    
    app.run(host='0.0.0.0', port=5000, debug=debug)

```

To run the backend_api using python3.10:

- Create a python virtual environment - only 1 time needed
```bash
python3.10 -m venv venv
source venv/bin/activate
chmod +x ./build.sh
chmod +x ./run.sh
export FLASK_ENV=development
export EXTERNAL_INTEGRATION_KEY=MY_INTEGRATION_KEY
./run.sh

```

- Activate the environment and configure - only 1 time needed
```bash
source venv/bin/activate
chmod +x ./build.sh
chmod +x ./run.sh
export FLASK_ENV=development
export EXTERNAL_INTEGRATION_KEY=MY_INTEGRATION_KEY
```

- Run the Application
```bash
./run.sh
```