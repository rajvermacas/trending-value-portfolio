# Conda

## Create environment
```bash
conda env create -f conda-env.yml
```

## Activate environment
```bash
conda activate env-name
```

## Deactivate environment
```bash
conda deactivate
```

## Remove environment
```bash
conda remove -n env-name --all
```

## Export environment
```bash
conda env export > conda-env.yml
```

# Acknowledgements
- This project is only intended for educational purposes. 
- We do not encourage or promote the use of this software in any illegal activities.
- We do not take any responsibility for any misuse of this software.

# VSCode debugging
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Local Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "args": ["--local"]
        },
        {
            "name": "Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}