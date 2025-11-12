"""Generate a sbatch .sb file based on the input arguments"""

import argparse
import os


def sbatch(email, name, time, memory, conda_env, path, node):
    """Generate sbatch script str"""
    sbatch_script = [
        "#!/bin/bash --login",
        "#SBATCH --mail-type=FAIL",
        f"#SBATCH --mail-user={email}",
        f"#SBATCH --job-name={name}",
        f"#SBATCH -o out/{name}/%A.out",
        f"#SBATCH --time={time}",
        f"#SBATCH --mem-per-cpu={memory}",
        f"conda activate {conda_env}",
        f"cd {path}",
        "python3 -m $*",
        "",
    ]
    if node is not None:
        sbatch_script.insert(1, f"#SBATCH -A {node}")
    return "\n".join(sbatch_script)


def main():
    """Generate and save sbatch script based on input arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-mail", "--email", type=str)
    parser.add_argument("-name", "--job_name", type=str, default="spatialegt")
    parser.add_argument("-time", "--time", type=str, default="0-03:59")
    parser.add_argument("-mem", "--memory", type=str, default="4gb")
    parser.add_argument("-env", "--conda_env", type=str, default="spatial_egt")
    parser.add_argument("-path", "--path", type=str, default=None)
    parser.add_argument("-node", "--node", type=str, default=None)
    args = parser.parse_args()

    path = args.path
    if path is None:
        path = os.getcwd().replace(" ", "\ ")

    script = sbatch(
        args.email, args.job_name, args.time, args.memory, args.conda_env, path, args.node
    )
    if not os.path.exists(f"out/{args.job_name}"):
        os.makedirs(f"out/{args.job_name}")
    with open(f"job_{args.job_name}.sb", "w", encoding="UTF-8") as f:
        f.write(script)


if __name__ == "__main__":
    main()
