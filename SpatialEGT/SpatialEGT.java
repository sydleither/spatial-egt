package SpatialEGT;

import java.lang.Math;
import java.nio.file.Paths;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;

import HAL.Gui.GridWindow;
import HAL.Tools.FileIO;
import HAL.Rand;

public class SpatialEGT {
    public static int[] GetPopulationSize(Model2D model) {
        int numResistant = 0;
        int numSensitive = 0;
        for (Cell2D cell : model) {
            if (cell.type == 0) {
                numSensitive += 1;
            }
            else {
                numResistant += 1;
            }
        }
        int[] popSize = new int[]{numSensitive, numResistant};
        return popSize;
    }

    public static int[] GetPopulationSize(Model0D model) {
        int numResistant = 0;
        int numSensitive = 0;
        for (Cell0D cell : model) {
            if (cell.type == 0) {
                numSensitive += 1;
            }
            else {
                numResistant += 1;
            }
        }
        int[] popSize = new int[]{numSensitive, numResistant};
        return popSize;
    }

    public static int[] GetPopulationSize(Model3D model) {
        int numResistant = 0;
        int numSensitive = 0;
        for (Cell3D cell : model) {
            if (cell.type == 0) {
                numSensitive += 1;
            }
            else {
                numResistant += 1;
            }
        }
        int[] popSize = new int[]{numSensitive, numResistant};
        return popSize;
    }

    public static void RunModels(String exp_name, String exp_dir, String rep, String dimension, Model2D nullModel, Model2D adaptiveModel, Model2D continuousModel, GridWindow win, FileIO popsOut, int numDays, boolean visualize, int granularity) {
        for (int tick = 0; tick <= numDays; tick++) {
            if (tick % 2 == 0) {
                int[] nullPop = GetPopulationSize(nullModel);
                int[] adaptivePop = GetPopulationSize(adaptiveModel);
                int[] continuousPop = GetPopulationSize(continuousModel);
                popsOut.Write(tick+","+nullPop[0]+","+nullPop[1]+","+adaptivePop[0]+","+adaptivePop[1]+","+continuousPop[0]+","+continuousPop[1]+"\n");
            }

            if (visualize) {
                nullModel.DrawModel(win, 0);
                adaptiveModel.DrawModel(win, 1);
                continuousModel.DrawModel(win, 2);
                if (tick % (int)(numDays/granularity) == 0) {
                    win.ToPNG("output/"+exp_dir+"/"+exp_name+"/"+rep+"/"+dimension+"model_tick"+tick+".png");
                }
            }

            nullModel.ModelStep();
            adaptiveModel.ModelStep();
            continuousModel.ModelStep();
        }
    }

    public static void RunModels(String exp_name, String exp_dir, String rep, String dimension, Model0D nullModel, Model0D adaptiveModel, Model0D continuousModel, GridWindow win, FileIO popsOut, int numDays, boolean visualize, int granularity) {
        for (int tick = 0; tick <= numDays; tick++) {
            if (tick % 2 == 0) {
                int[] nullPop = GetPopulationSize(nullModel);
                int[] adaptivePop = GetPopulationSize(adaptiveModel);
                int[] continuousPop = GetPopulationSize(continuousModel);
                popsOut.Write(tick+","+nullPop[0]+","+nullPop[1]+","+adaptivePop[0]+","+adaptivePop[1]+","+continuousPop[0]+","+continuousPop[1]+"\n");
            }

            if (visualize) {
                nullModel.DrawModel(win, 0);
                adaptiveModel.DrawModel(win, 1);
                continuousModel.DrawModel(win, 2);
                if (tick % (int)(numDays/granularity) == 0) {
                    win.ToPNG("output/"+exp_dir+"/"+exp_name+"/"+rep+"/"+dimension+"model_tick"+tick+".png");
                }
            }

            nullModel.ModelStep();
            adaptiveModel.ModelStep();
            continuousModel.ModelStep();
        }
    }

    public static void RunModels(Model3D nullModel, Model3D adaptiveModel, Model3D continuousModel, FileIO popsOut, int numDays) {
        for (int tick = 0; tick <= numDays; tick++) {
            if (tick % 2 == 0) {
                int[] nullPop = GetPopulationSize(nullModel);
                int[] adaptivePop = GetPopulationSize(adaptiveModel);
                int[] continuousPop = GetPopulationSize(continuousModel);
                popsOut.Write(tick+","+nullPop[0]+","+nullPop[1]+","+adaptivePop[0]+","+adaptivePop[1]+","+continuousPop[0]+","+continuousPop[1]+"\n");
            }

            nullModel.ModelStep();
            adaptiveModel.ModelStep();
            continuousModel.ModelStep();
        }
    }

    public static void main(String[] args) {
        String exp_dir = args[0];
        String exp_name = args[1];
        String dimension = args[2];
        String rep = args[3];
        boolean visualize = args[4].equals("visualize");
        int granularity = 10;
        if (visualize)
            granularity = Integer.parseInt(args[5]);
        
        ObjectMapper mapper = new ObjectMapper();
        Map<String, Object> params;
        try{
            params = mapper.readValue(Paths.get("output/"+exp_dir+"/"+exp_name+"/"+exp_name+".json").toFile(), Map.class);
        }
        catch (Exception e) {
            return;
        }

        int visScale = 4;
        int numDays = (int) params.get("numDays");
        int x = (int) params.get("x");
        int y = (int) params.get("y");
        int neighborhood = (int) params.get("neighborhoodRadius");
        double deathRate = (double) params.get("deathRate");
        double drugGrowthReduction = (double) params.get("drugGrowthReduction");
        int numCells = (int) params.get("numCells");
        double proportionResistant = (double) params.get("proportionResistant");
        double adaptiveTreatmentThreshold = (double) params.get("adaptiveTreatmentThreshold");
        double[][] payoff = new double[2][2];
        payoff[0][0] = (double) params.get("A");
        payoff[0][1] = (double) params.get("B");
        payoff[1][0] = (double) params.get("C");
        payoff[1][1] = (double) params.get("D");

        GridWindow win = null;
        if (visualize)
            win = new GridWindow(dimension+" null vs adaptive vs continuous", x*3, y, visScale);
        FileIO popsOut = new FileIO("output/"+exp_dir+"/"+exp_name+"/"+rep+"/"+dimension+"populations.csv", "w");
        popsOut.Write("time,null_sensitive,null_resistant,adaptive_sensitive,adaptive_resistant,continuous_sensitive,continuous_resistant\n");

        if (dimension.equals("2D")) {
            Model2D nullModel = new Model2D(x, y, new Rand(), neighborhood, deathRate, 0.0, false, 0.0, payoff);
            Model2D adaptiveModel = new Model2D(x, y, new Rand(), neighborhood, deathRate, drugGrowthReduction, true, adaptiveTreatmentThreshold, payoff);
            Model2D continuousModel = new Model2D(x, y, new Rand(), neighborhood, deathRate, drugGrowthReduction, false, 0.0, payoff);
            nullModel.InitTumorRandom(numCells, proportionResistant);
            adaptiveModel.InitTumorRandom(numCells, proportionResistant);
            continuousModel.InitTumorRandom(numCells, proportionResistant);    
            RunModels(exp_name, exp_dir, rep, dimension, nullModel, adaptiveModel, continuousModel, win, popsOut, numDays, visualize, granularity);
        }
        else if (dimension.equals("WM")) {
            Model0D nullModel = new Model0D(x, y, new Rand(), deathRate, 0.0, false, 0.0, payoff);
            Model0D adaptiveModel = new Model0D(x, y, new Rand(), deathRate, drugGrowthReduction, true, adaptiveTreatmentThreshold, payoff);
            Model0D continuousModel = new Model0D(x, y, new Rand(), deathRate, drugGrowthReduction, false, 0.0, payoff);
            nullModel.InitTumorRandom(numCells, proportionResistant);
            adaptiveModel.InitTumorRandom(numCells, proportionResistant);
            continuousModel.InitTumorRandom(numCells, proportionResistant);    
            RunModels(exp_name, exp_dir, rep, dimension, nullModel, adaptiveModel, continuousModel, win, popsOut, numDays, visualize, granularity);
        }
        else if (dimension.equals("3D")) {
            int totalCells = x*y;
            int z = (int)Math.cbrt(totalCells);
            Model3D nullModel = new Model3D(z, z, z, new Rand(), neighborhood, deathRate, 0.0, false, 0.0, payoff);
            Model3D adaptiveModel = new Model3D(z, z, z, new Rand(), neighborhood, deathRate, drugGrowthReduction, true, adaptiveTreatmentThreshold, payoff);
            Model3D continuousModel = new Model3D(z, z, z, new Rand(), neighborhood, deathRate, drugGrowthReduction, false, 0.0, payoff);
            nullModel.InitTumorRandom(numCells, proportionResistant);
            adaptiveModel.InitTumorRandom(numCells, proportionResistant);
            continuousModel.InitTumorRandom(numCells, proportionResistant);    
            RunModels(nullModel, adaptiveModel, continuousModel, popsOut, numDays);
        }

        popsOut.Close();
        if (visualize)
            win.Close();
    }
}
