package SpatialEGT;

import java.util.Arrays;
import java.lang.Math;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;

import HAL.Gui.GifMaker;
import HAL.Gui.GridWindow;
import HAL.Tools.FileIO;
import HAL.Rand;
import HAL.Util;

public class SpatialEGT2D {
    public static HashMap<Integer,Double> GetFsList(Model2D model, int maxRadius) {
        HashMap<Integer,Double> fsList = new HashMap<Integer,Double>();
        for (int radius = 1; radius < maxRadius; radius++) {
            fsList.put(radius, 0.0);
        }
        int numCells = 0;
        for (Cell2D cell : model) {
            if (cell.type == 0) {
                continue;
            }
            HashMap<Integer,Double> fsListCell = cell.Fs(maxRadius);
            for (int radius = 1; radius < maxRadius; radius++) {
                fsList.put(radius, fsList.get(radius)+fsListCell.get(radius));
            }
            numCells += 1;
        }
        for (int radius = 1; radius < maxRadius; radius++) {
            fsList.put(radius, fsList.get(radius)/numCells);
        }
        return fsList;
    }

    public static Map<Integer, Integer[]> GetPairCorrelation(Model2D model, int maxDistance, int area, Map<List<Integer>, Integer> annulusAreaLookupTable, int start, int length) {
        List<Cell2D> cells = new ArrayList<Cell2D>();
        for (Cell2D cell : model) {
            cells.add(cell);
        }

        Map<Integer, Integer[]> annulusRow = new HashMap<>();
        for (int i = 1; i < maxDistance; i++) {
            Integer annulusStartingList[] = {0, 0, 0, 0};
            annulusRow.put(i, annulusStartingList);
        }

        for (int a = 0; a < cells.size(); a++) {
            for (int b = 0; b < cells.size(); b++) {
                if (a == b) {
                    continue;
                }

                Cell2D cellA = cells.get(a);
                Cell2D cellB = cells.get(b);
                int cellAtype = cellA.type;
                int cellBtype = cellB.type;
                int xDistance = Math.abs(cellA.Xsq() - cellB.Xsq());
                int yDistance = Math.abs(cellA.Ysq() - cellB.Ysq());
                int annulus = xDistance + yDistance;

                if (cellA.Xsq() >= start+length || cellA.Xsq() <= start) {
                    continue;
                }
                if (cellA.Ysq() >= start+length || cellA.Ysq() <= start) {
                    continue;
                }
                if (cellB.Xsq() >= start+length || cellB.Xsq() <= start) {
                    continue;
                }
                if (cellB.Ysq() >= start+length || cellB.Ysq() <= start) {
                    continue;
                }

                if (annulus >= maxDistance) {
                    continue;
                }

                int pairType;
                if (cellAtype == 0 && cellBtype == 0)
                    pairType = 0;
                else if (cellAtype == 1 && cellBtype == 1)
                    pairType = 1;
                else if (cellAtype == 1 && cellBtype == 0)
                    pairType = 2;
                else if (cellAtype == 0 && cellBtype == 1)
                    pairType = 3;
                else
                    pairType = -9;

                List<Integer> tableKey = Arrays.asList(cellA.Xsq(), cellA.Ysq(), annulus);
                int normalized_count = (int)(area/annulusAreaLookupTable.get(tableKey));
                annulusRow.get(annulus)[pairType] = annulusRow.get(annulus)[pairType]+normalized_count;
            }
        }

        return annulusRow;
    }

    public static Map<List<Integer>, Integer> GetAnnulusAreaLookupTable(int start, int length, int maxDistance) {
        //TODO make more efficient (don't calculate area when radius is not near boundary, reflections)
        Map<List<Integer>, Integer> table = new HashMap<>();
        for (int r = 1; r < maxDistance; r++) {
            for (int x1 = start; x1 < length+start; x1++) {
                for (int y1 = start; y1 < length+start; y1++) {
                    List<Integer> tableKey = Arrays.asList(x1, y1, r);
                    int area = 0;
                    for (int x2 = Math.max(x1-r,start); x2 <= Math.min(x1+r,start+length); x2++) {
                        for (int y2 = Math.max(y1-r,start); y2 <= Math.min(y1+r,start+length); y2++) {
                            if (Math.abs(x1-x2) + Math.abs(y1-y2) == r) {
                                area += 1;
                            }
                        }
                    }
                    table.put(tableKey, area);
                }
            }
        }
        return table;
    }

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

    public SpatialEGT2D(String saveLoc, Map<String, Object> params, long seed, int visualizationFrequency) {
        // turn parameters json into variables
        int runNull = (int) params.get("null");
        int runContinuous = (int) params.get("continuous");
        int runAdaptive = (int) params.get("adaptive");
        int writePopFrequency = (int) params.get("writePopFrequency");
        int writePcFrequency = (int) params.get("writePcFrequency");
        int writeFsFrequency = (int) params.get("writeFsFrequency");
        int numTicks = (int) params.get("numTicks");
        int x = (int) params.get("x");
        int y = (int) params.get("y");
        int neighborhood = (int) params.get("neighborhoodRadius");
        double deathRate = (double) params.get("deathRate");
        double drugGrowthReduction = (double) params.get("drugGrowthReduction");
        int numCells = (int) params.get("numCells");
        double proportionResistant = (double) params.get("proportionResistant");
        double adaptiveTreatmentThreshold = (double) params.get("adaptiveTreatmentThreshold");
        int initialTumor = (int) params.get("initialTumor");
        double[][] payoff = new double[2][2];
        payoff[0][0] = (double) params.get("A");
        payoff[0][1] = (double) params.get("B");
        payoff[1][0] = (double) params.get("C");
        payoff[1][1] = (double) params.get("D");

        // calculations for pair correlation
        int maxDistance = 0;
        Map<List<Integer>, Integer> annulusAreaLookupTable = null;

        // initialize with specified models
        HashMap<String,Model2D> models = new HashMap<String,Model2D>();
        if (runNull == 1) {
            Model2D nullModel = new Model2D(x, y, new Rand(seed), neighborhood, deathRate, 0.0, false, 0.0, payoff);
            models.put("nodrug", nullModel);
        }
        if (runContinuous == 1) {
            Model2D continuousModel = new Model2D(x, y, new Rand(seed), neighborhood, deathRate, drugGrowthReduction, false, 0.0, payoff);
            models.put("continuous", continuousModel);
        }
        if (runAdaptive == 1) {
            Model2D adaptiveModel = new Model2D(x, y, new Rand(seed), neighborhood, deathRate, drugGrowthReduction, true, adaptiveTreatmentThreshold, payoff);
            models.put("adaptive", adaptiveModel);
        }

        // check what to run and initialize output
        boolean writePop = writePopFrequency != 0;
        boolean writePc = writePcFrequency != 0;
        boolean writeFs = writeFsFrequency != 0;
        boolean visualize = visualizationFrequency != 0;

        GridWindow win = null;
        GifMaker gifWin = null;
        if (visualize) {
            win = new GridWindow("SpatialEGT", x, y, 4);
            gifWin = new GifMaker(saveLoc+"growth.gif", 0, false);
            writePop = false;
            writePc = false;
            writeFs = false;
        }
        FileIO popsOut = null;
        if (writePop) {
            popsOut = new FileIO(saveLoc+"populations.csv", "w");
            popsOut.Write("model,time,sensitive,resistant\n");
        }
        FileIO pcOut = null;
        if (writePc) {
            maxDistance = 20;
            annulusAreaLookupTable = GetAnnulusAreaLookupTable(60, 10, maxDistance);
            pcOut = new FileIO(saveLoc+"pairCorrelations.csv", "w");
            pcOut.Write("model,time,pair,measure,radius,normalized_count\n");
        }
        FileIO fsOut = null;
        if (writeFs) {
            fsOut = new FileIO(saveLoc+"fs.csv", "w");
            fsOut.Write("model,time,radius,fs\n");
        }
        
        // run models
        for (Map.Entry<String,Model2D> modelEntry : models.entrySet()) {
            String modelName = modelEntry.getKey();
            Model2D model = modelEntry.getValue();
            if (initialTumor == 1)
                model.InitTumorLinear(numCells, proportionResistant);
            else if (initialTumor == 2)
                model.InitTumorConvex(numCells, proportionResistant);
            else if (initialTumor == 3)
                model.InitTumorConcave(numCells, proportionResistant);
            else if (initialTumor == 4)
                model.InitTumorCluster(numCells, proportionResistant);
            else
                model.InitTumorRandom(numCells, proportionResistant);

            for (int tick = 0; tick <= numTicks; tick++) {
                if (writePop) {
                    if (tick % writePopFrequency == 0) {
                        int[] pop = GetPopulationSize(model);
                        popsOut.Write(modelName+","+tick+","+pop[0]+","+pop[1]+"\n");
                    }
                }
                if (writePc) {
                    if (tick % writePcFrequency == 0) {
                        Map<Integer, Integer[]> annulusRows = GetPairCorrelation(model, maxDistance, x*y, annulusAreaLookupTable, 60, 10);
                        String pairTypes[] = {"SS", "RR", "RS", "SR"};
                        for (int dist = 1; dist < maxDistance; dist++) {
                            for (int i = 0; i < 4; i++) {
                                pcOut.Write(modelName+","+tick+","+pairTypes[i]+",annulus,"+dist+","+annulusRows.get(dist)[i]+"\n");
                            }
                        }
                    }
                }
                if (writeFs) {
                    if (tick % writeFsFrequency == 0) {
                        HashMap<Integer,Double> fsList = GetFsList(model, 10);
                        for (Map.Entry<Integer,Double> entry : fsList.entrySet()) {
                            int radius = entry.getKey();
                            double fs = entry.getValue();
                            fsOut.Write(modelName+","+tick+","+radius+","+fs+"\n");
                        }
                    }
                }
                if (visualize) {
                    model.DrawModel(win, 0);
                    if (tick % visualizationFrequency == 0) {
                        win.ToPNG(saveLoc+modelName+tick+".png");
                    }
                    gifWin.AddFrame(win);
                }
                model.ModelStep();
            }
        }

        // close output files
        if (visualize) {
            win.Close();
            gifWin.Close();
        }
        if (writePop) {
            popsOut.Close();
        }
        if (writePc) {
            pcOut.Close();
        }
        if (writeFs) {
            fsOut.Close();
        }
    }
}
