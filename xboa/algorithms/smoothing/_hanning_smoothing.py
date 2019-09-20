import copy

class HanningSmoothing(object):
    def __init__(self):
        pass

    def smooth(self, data):
        omega = math.pi*len(data)
        data_out = copy.deepcopy(data)
        for i_index, item in enumerate(data):
            x_smoothed = data[index]
            for j_index, item in enumerate(data):
                x_smoothed += data[j_index]*cos(omega*(j_index-i_index))**2.
            data_out[index] = x_smoothed
        return data_out
