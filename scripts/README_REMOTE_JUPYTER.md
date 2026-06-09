# Remote Jupyter helper scripts

Files added:

- `scripts/remote_start_sage_jupyter.sh` - install this on `knuth` (e.g. `~/bin/remote_start_sage_jupyter.sh`).
- `scripts/local_start_and_forward.sh` - run on your *local* machine to install the remote helper (if needed), start Jupyter and create a background local tunnel.

Recommended (local-driven) workflow

1. From your local machine run:

   ```bash
   scripts/local_start_and_forward.sh youruser@knuth 8888 8888
   ```

   This will:
   - copy `remote_start_sage_jupyter.sh` to `~/bin/` on `knuth` if not present,
   - start Sage/Jupyter there (in `tmux` if available, otherwise via `nohup`),
   - create a backgrounded SSH tunnel (`ssh -f -N -L ...`) to forward `localhost:8888`.

2. The script prints a local URL with the token to open in your browser.

Remote-only workflow (if your local machine runs an SSH server reachable from `knuth`)

1. Install `remote_start_sage_jupyter.sh` on knuth (e.g. `~/bin/remote_start_sage_jupyter.sh`) and make it executable.
2. From knuth run:

   ```bash
   ~/bin/remote_start_sage_jupyter.sh 8888 ~/jupyter.log jupyter --reverse yourlocaluser@your.local.host:9000
   ```

   This attempts to establish an `ssh -R` reverse tunnel from knuth to your local machine so you can open `http://localhost:9000` locally. This only works if your local machine is reachable from the remote host and SSH keys/permissions allow remote port forwarding.

Notes & security

- Prefer the local-driven workflow (the `local_start_and_forward.sh`) because it uses an SSH tunnel initiated from your machine (secure, simple).
- Reverse tunnels require your local machine to be reachable by the remote host (and SSH `GatewayPorts`/`AllowTcpForwarding` may need to be enabled).
- Do not bind Jupyter to `0.0.0.0` unless you understand the security implications.
