import json
import os
import sys


def experiment_config(exp_dir, config_name, runNull, runAdaptive, runContinuous, writePopFrequency, writeFsFrequency,
                      writePcFrequency, numTicks, radius, deathRate, drugGrowthReduction, numCells, 
                      proportionResistant, adaptiveTreatmentThreshold, initialTumor, toyGap, payoff):
    config = {
        "null": runNull,
        "adaptive": runAdaptive,
        "continuous": runContinuous,
        "visualizationFrequency": 0,
        "writePopFrequency": writePopFrequency,
        "writePcFrequency": writePcFrequency,
        "writeFsFrequency": writeFsFrequency,
        "x": 125,
        "y": 125,
        "neighborhoodRadius": radius,
        "numTicks": numTicks,
        "deathRate": deathRate,
        "drugGrowthReduction": drugGrowthReduction,
        "numCells": numCells,
        "proportionResistant": proportionResistant,
        "adaptiveTreatmentThreshold": adaptiveTreatmentThreshold,
        "initialTumor": initialTumor,
        "toyGap": toyGap,
        "A": payoff[0],
        "B": payoff[1],
        "C": payoff[2],
        "D": payoff[3]
    }

    config_path = f"output/{exp_dir}/{config_name}/{config_name}.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def initial_games(exp_dir, names, bmws, bwms, gw=0.03, runNull=1, runAdaptive=0, runContinuous=1, writePopFrequency=1, writeFsFrequency=0,
                  writePcFrequency=500, radius=1, turnover=0.009, drug_reduction=0.5, init_cells=4375, prop_res=0.01, 
                  adaptiveTreatmentThreshold=0.5, initialTumor=0, toyGap=5, runtime=50000):
    if not os.path.exists("output/"+exp_dir):
        os.mkdir("output/"+exp_dir)
    config_names = []

    gm = 0.8*gw

    for i in range(len(names)):
        bmw = bmws[i]
        bwm = bwms[i]
        payoff = [gw, round(gw+bwm, 3), round(gm+bmw, 3), gm]

        exp_name = names[i]
        os.mkdir("output/"+exp_dir+"/"+exp_name)
        for i in range(10):
            os.mkdir("output/"+exp_dir+"/"+exp_name+"/"+str(i))
        experiment_config(exp_dir, exp_name, runNull, runAdaptive, runContinuous, writePopFrequency, writeFsFrequency,
                          writePcFrequency, runtime, radius, turnover, drug_reduction, init_cells, 
                          prop_res, adaptiveTreatmentThreshold, initialTumor, toyGap, payoff)
        config_names.append(exp_name)

    submit_output, analysis_output = generate_scripts_batch(exp_dir, config_names)
    return submit_output, analysis_output


def custom_games(exp_dir, names, a, b, c, d, runNull=1, runAdaptive=0, runContinuous=1, writePopFrequency=1, writeFsFrequency=0,
                  writePcFrequency=500, radius=1, turnover=0.009, drug_reduction=0.5, init_cells=4375, prop_res=0.01, 
                  adaptiveTreatmentThreshold=0.5, initialTumor=0, toyGap=5, runtime=500, replicates=10, spaces=["2D", "3D", "WM"]):
    if not os.path.exists("output/"+exp_dir):
        os.makedirs("output/"+exp_dir)
    config_names = []

    for i in range(len(names)):
        payoff = [a[i], b[i], c[i], d[i]]

        exp_name = names[i]
        os.mkdir("output/"+exp_dir+"/"+exp_name)
        for i in range(replicates):
            os.mkdir("output/"+exp_dir+"/"+exp_name+"/"+str(i))
        experiment_config(exp_dir, exp_name, runNull, runAdaptive, runContinuous, writePopFrequency, writeFsFrequency,
                          writePcFrequency, runtime, radius, turnover, drug_reduction, init_cells, 
                          prop_res, adaptiveTreatmentThreshold, initialTumor, toyGap, payoff)
        config_names.append(exp_name)

    submit_output, analysis_output = generate_scripts_batch(exp_dir, config_names, spaces)
    return submit_output, analysis_output


def generate_scripts_batch(exp_dir, config_names, spaces):
    submit_output = []
    analysis_output = []
    for config_name in config_names:
        for space in spaces:
            if space == "WM":
                config_type = "long"
            else:
                config_type = "short"
            submit_output.append(f"sbatch run_config_{config_type}.sb {exp_dir} {config_name} {space}\n")
            analysis_output.append(f"java -cp build/:lib/* SpatialEGT.SpatialEGT {exp_dir} {config_name} {space} 0 2000\n")
    return submit_output, analysis_output


def write_scripts_batch(exp_dir, submit_output, analysis_output):
    with open(f"output/run_{exp_dir}_experiments", "w") as f:
        for output_line in submit_output:
            f.write(output_line)

    with open(f"output/analyze_{exp_dir}_experiments", "w") as f:
        for output_line in analysis_output:
            f.write(output_line)


if __name__ == "__main__":
    experiment_name = sys.argv[1]
    submit_output = []
    analysis_output = []
    if experiment_name == "games":
        names = ["competition", "no_game", "coexistance"]
        bmws = [-0.007, 0, 0.007]
        bwms = [0.0, 0.0, 0.0]
        s, a = initial_games(experiment_name, names, bmws, bwms, runtime=10000)
        submit_output += s
        analysis_output += a
    elif experiment_name == "coexist":
        names = ["14", "25", "33", "40", "45", "50", "60", "70", "80", "90"]
        bmws = [0.007, 0.008, 0.009, 0.010, 0.011, 0.012, 0.015, 0.020, 0.030, 0.060]
        bwms = [0.0]*len(bmws)
        s, a = initial_games(experiment_name, names, bmws, bwms)
        submit_output += s
        analysis_output += a
    elif experiment_name == "gameshood":
        names = ["competition", "no_game", "coexistance"]
        bmws = [-0.007, 0, 0.007]
        bwms = [0.0, 0.0, 0.0]
        for radius in [1, 2, 3, 4, 5]:
            s, a = initial_games(experiment_name, [x+str(radius) for x in names], bmws, bwms, radius=radius)
            submit_output += s
            analysis_output += a
    elif experiment_name == "gamespc_all":
        games = ["sensitive", "coexistence", "bistability", "resistant"]
        betas = [["max", "half", "zero", "min"], ["25", "50", "75"], ["25", "50", "75"], ["min", "half", "max"]]
        bmws = [[0.005, 0.00025, 0.0, -0.024], [0.008, 0.012, 0.024], [0.00133, -0.008, -0.036], [0.004, 0.0455, 0.087]]
        bwms = [[0.0]*4, [0.0]*3, [-0.02]*3, [-0.004]*3]
        gws = [0.03, 0.03, 0.03, 0.015]
        for i in range(len(games)):
            names = [games[i]+"_"+betas[i][x] for x in range(len(betas[i]))]
            s, a = initial_games(experiment_name, names, bmws[i], bwms[i], gw=gws[i], init_cells=100, 
                                 prop_res=0.05, runtime=500, runContinuous=0, writePcFrequency=100, radius=3)
            submit_output += s
            analysis_output += a
    elif experiment_name == "custom_gamespc_all":
        games = ["sensitive", "coexistence", "bistability", "resistant"]
        subgames = [["agtb", "bgta", "equal"], ["bgtc", "cgtb", "equal"],
                    ["equal", "agtd", "dgta"], ["cgtd", "dgtc", "equal"]]
        pa = [[0.09, 0.06, 0.06], [0.03, 0.06, 0.03], [0.06, 0.09, 0.06], [0.06, 0.03, 0.03]]
        pb = [[0.06, 0.09, 0.06], [0.09, 0.06, 0.06], [0.03, 0.03, 0.06], [0.03, 0.06, 0.03]]
        pc = [[0.06, 0.03, 0.03], [0.06, 0.09, 0.06], [0.03, 0.06, 0.03], [0.09, 0.06, 0.06]]
        pd = [[0.03, 0.06, 0.03], [0.06, 0.03, 0.03], [0.06, 0.06, 0.09], [0.06, 0.09, 0.06]]
        for i in range(len(games)):
            names = [games[i]+"_"+subgames[i][x] for x in range(len(subgames[i]))]
            s, a = custom_games(experiment_name, names, a=pa[i], b=pb[i], c=pc[i], d=pd[i], initialTumor=0, turnover=0.009,
                                 init_cells=1250, prop_res=0.5, runtime=100, runContinuous=0, writePcFrequency=25, radius=3)
            submit_output += s
            analysis_output += a
    elif experiment_name == "at_paramsweep":
        names = ["competition", "nogame", "coexistence"]
        bmws = [-0.007, 0, 0.007]
        bwms = [0.0, 0.0, 0.0]
        for i,threshold in enumerate([0.3, 0.5, 0.7]):
            for j,fr in enumerate([0.01, 0.05, 0.1]):
                for k,cells in enumerate([1875, 6250, 11250]):
                    subexp_names = [f"{x}_thr{i}_fr{j}_c{k}" for x in names]
                    s, a = initial_games(experiment_name, subexp_names, bmws, bwms,
                                         radius=2, runAdaptive=1, writePcFrequency=0,
                                         drug_reduction=0.9, init_cells=cells, prop_res=fr, 
                                         adaptiveTreatmentThreshold=threshold, runtime=10000)
                    submit_output += s
                    analysis_output += a
    elif experiment_name == "at_gamesweep":
        names = ["competition", "no_game", "coexistence"]
        bmws = [-0.007, 0, 0.007]
        bwms = [0.0, 0.0, 0.0]
        s, a = initial_games(experiment_name, names, bmws, bwms, runNull=1, runContinuous=0,
                                radius=3, runAdaptive=0, writePcFrequency=0, writeFsFrequency=2,
                                drug_reduction=0.9, init_cells=11250, prop_res=0.01,
                                adaptiveTreatmentThreshold=0.3, runtime=50)
        submit_output += s
        analysis_output += a
    elif experiment_name == "gaps_linear":
        games = ["sensitive", "coexistence", "bistability", "resistant"]
        subgames = [["agtb", "bgta", "equal"], ["bgtc", "cgtb", "equal"],
                    ["equal", "agtd", "dgta"], ["cgtd", "dgtc", "equal"]]
        pa = [[0.09, 0.06, 0.06], [0.03, 0.06, 0.03], [0.06, 0.09, 0.06], [0.06, 0.03, 0.03]]
        pb = [[0.06, 0.09, 0.06], [0.09, 0.06, 0.06], [0.03, 0.03, 0.06], [0.03, 0.06, 0.03]]
        pc = [[0.06, 0.03, 0.03], [0.06, 0.09, 0.06], [0.03, 0.06, 0.03], [0.09, 0.06, 0.06]]
        pd = [[0.03, 0.06, 0.03], [0.06, 0.03, 0.03], [0.06, 0.06, 0.09], [0.06, 0.09, 0.06]]
        for i in range(len(games)):
            names = [games[i]+"_"+subgames[i][x] for x in range(len(subgames[i]))]
            s, a = custom_games(writePopFrequency=1, writeFsFrequency=500,
                                exp_dir=experiment_name, names=names, a=pa[i], b=pb[i], c=pc[i], d=pd[i], initialTumor=1, turnover=0.018,
                                init_cells=15625, prop_res=0.5, runtime=2000, runContinuous=0, writePcFrequency=500, radius=3, toyGap=5)
            submit_output += s
            analysis_output += a
    elif experiment_name == "sample1":
        games = ["sensitive", "coexistence", "bistability", "resistant"]
        subgames = [["agtb", "bgta", "equal"], ["bgtc", "cgtb", "equal"],
                    ["equal", "agtd", "dgta"], ["cgtd", "dgtc", "equal"]]
        pa = [[0.09, 0.06, 0.06], [0.03, 0.06, 0.03], [0.06, 0.09, 0.06], [0.06, 0.03, 0.03]]
        pb = [[0.06, 0.09, 0.06], [0.09, 0.06, 0.06], [0.03, 0.03, 0.06], [0.03, 0.06, 0.03]]
        pc = [[0.06, 0.03, 0.03], [0.06, 0.09, 0.06], [0.03, 0.06, 0.03], [0.09, 0.06, 0.06]]
        pd = [[0.03, 0.06, 0.03], [0.06, 0.03, 0.03], [0.06, 0.06, 0.09], [0.06, 0.09, 0.06]]
        for fr in [0.2, 0.4, 0.6, 0.8]:
            for cells in [3125, 6250, 9375, 12500]:
                for i in range(len(games)):
                    names = [games[i]+"_"+subgames[i][x] for x in range(len(subgames[i]))]
                    exp_dir = f"{experiment_name}/fr{str(fr)[-1]}_c{cells}"
                    s, a = custom_games(writePopFrequency=250, writeFsFrequency=250, exp_dir=exp_dir, 
                                        names=names, a=pa[i], b=pb[i], c=pc[i], d=pd[i], initialTumor=0, 
                                        turnover=0.009, init_cells=cells, prop_res=fr, runtime=250, 
                                        runContinuous=0, writePcFrequency=0, radius=2, replicates=3,
                                        spaces=["2D"])
                    submit_output += s
                    analysis_output += a
    else:
        print("Invalid experiment name.")
        exit()
    write_scripts_batch(experiment_name, submit_output, analysis_output)
    print("Make sure you recompile SpatialEGT before pushing jobs:")
    print("javac -d \"build\" -cp \"lib/*\" @sources.txt")
