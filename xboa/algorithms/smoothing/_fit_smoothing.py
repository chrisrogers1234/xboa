import copy
import ROOT

class FitSmoothing(object):
    def __init__(self, fit_function):
        self.fit = fit_function

    def smooth(self, data):
        graph = ROOT.TGraph(len(data))
        for i, data_y in enumerate(data):
            graph.SetPoint(i, i, data_y)
        graph.Fit(self.fit)
        data_out = [self.fit.Eval(i) for i in range(len(data))]
        return data_out

