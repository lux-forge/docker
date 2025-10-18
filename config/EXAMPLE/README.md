# Config Setup

To generate the environment variables, you need to copy the folders in EXAMPLE to this root dir of `./config/`.

I.e. change from this structure:
```
config/
├── EXAMPLE/
│   ├── global/
│   ├── nodes/
│   ├── ├── NODE1/.env
│   ├── ├── NODE2/.env
│   ├── ├── NODE3/.env

```

to this:
```
config/
├── global/
│   ├── global.env
├── nodes/
│   ├── NODE1/.env
│   ├── NODE2/.env
│   ├── NODE3/.env
```
