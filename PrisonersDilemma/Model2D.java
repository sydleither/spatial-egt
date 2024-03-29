package PrisonersDilemma;

import HAL.GridsAndAgents.AgentGrid2D;
import HAL.GridsAndAgents.AgentSQ2Dunstackable;
import HAL.Gui.GridWindow;
import HAL.Rand;
import HAL.Util;

public class Model2D extends AgentGrid2D<Cell2D> {
    public Rand rng;
    public int[] divHood = Util.VonNeumannHood(false);
    public int cost, benefit;
    public double divProb, deathProb;

    public Model2D(int x, int y, Rand rng, int cost, int benefit, double divProb, double deathProb) {
        super(x, y, Cell2D.class);
        this.rng = rng;
        this.cost = cost;
        this.benefit = benefit;
        this.divProb = divProb;
        this.deathProb = deathProb;
    }

    public void InitTumor(int radius, double defectorProportion) {
        int[] tumorHood = Util.CircleHood(true, radius);
        int hoodSize = MapHood(tumorHood, xDim/2, yDim/2);
        for (int i = 0; i < hoodSize; i++) {
            if (rng.Double() < defectorProportion) {
                NewAgentSQ(tumorHood[i]).Init(1);
            }
            else {
                NewAgentSQ(tumorHood[i]).Init(0);
            }
        }
    }

    public void ModelStep(int tick) {
        ShuffleAgents(rng);
        for (Cell2D cell : this) {
            cell.CellStep();
        }
    }

    public void DrawModel(GridWindow win, int iModel) {
        for (int x = 0; x < xDim; x++) {
            for (int y = 0; y < yDim; y++) {
                int color = Util.BLACK;
                Cell2D cell = GetAgent(x, y);
                if (cell != null) {
                    color = cell.color;
                }
                win.SetPix(x+iModel*xDim, y, color);
            }
        }
    }
}

class Cell2D extends AgentSQ2Dunstackable<Model2D> {
    public int type;
    public int color;

    public void Init(int type) {
        this.type = type;
        if (type == 0) {
            this.color = Util.RGB256(239, 124, 142);
        }
        else {
            this.color = Util.RGB256(76, 149, 108);
        }
    }

    public double GetPayoff() {
        int cooperators = 0;
        int[] interactionHood = Util.CircleHood(false, 2);
        int neighbors = MapOccupiedHood(interactionHood);
        if (neighbors == 0) {
            return 0.0;
        }
        for (int i = 0; i < neighbors; i++) {
            Cell2D neighborCell = G.GetAgent(i);
            if (neighborCell != null) {
                if (neighborCell.type == 0) {
                    cooperators += 1;
                }
            }
        } //TODO make sigmoidal
        double payoff = 0;
        if (this.type == 0) {
            payoff = ((G.benefit * (cooperators+1)) / neighbors) - G.cost;
        }
        else {
            payoff = (G.benefit * (cooperators)) / neighbors;
        }
        return payoff;
    }

    public void CellStep() {
        double payoff = this.GetPayoff();
        if (G.rng.Double() < G.deathProb - payoff/10) {
            Dispose();
            return;
        }
        if (G.rng.Double() < G.divProb) {
            int options = MapEmptyHood(G.divHood);
            if (options > 0) {
                G.NewAgentSQ(G.divHood[G.rng.Int(options)]).Init(this.type);
            }
        }
    }
}