import math
import cmath
import numpy
import copy

#citation: George Parzen 1995 "Linear Parameters and the Decoupling Matrix for
#          Linearly Coupled Motion in 6 Dimensional Phase Space",
#          arxiv:acc-phys/9510006, PAC 1997, DOI: 10.1109/PAC.1997.750716
class DecoupledTransferMatrix(object):
    """
    Calculates transformation for decoupling a 2N dimensional transfer matrix
    into N 2x2 transfer matrices.

    Once the decoupling transformation has been calculated, this can be used
    to deduce periodic solutions to the general beam ellipse problem, including
    periodic beta functions and generalised emittances.
    """
    def __init__(self, transfer_matrix):
        """
        Calculate the decoupling transformation
        - transfer_matrix: a 2Nx2N list of lists whose elements make up the
          transfer matrix. transfer_matrix should be symplectic, i.e.
          M S^T M^T S = I where S is the usual symplectic matrix.
        """
        self.m = numpy.array(transfer_matrix)
        if self.m.shape[0] != self.m.shape[1]:
            raise ValueError("Transfer matrix was not square")
        if (self.m.shape[0]/2)*2 != self.m.shape[0]:
            raise ValueError("Transfer matrix had odd size (should be even)")
        det_m = numpy.linalg.det(self.m)
        if abs(det_m - 1) > self.det_tolerance:
            raise ValueError("Transfer matrix determinant deviated from 1 by "+\
              str(det_m - 1)+" - DecoupledTransferMatrix.det_tolerance was "+\
              str(self.det_tolerance) )
        self.dim = self.m.shape[0]/2
        self.m_evalue, self.m_evector = numpy.linalg.eig(self.m)
        self.t_evector = None
        self.t_evalue = None
        self.t = None
        self.r = None
        self.v_t = None
        self.phase = [None]*self.dim
        self._get_decoupling()

    def _get_decoupling(self):
        """
        Calculate the transformation that decouples the transfer matrix and some
        other associated set-up.
        """
        self.t_evector = [[0+0j for i in range(self.dim*2)] for j in range(self.dim*2)]
        self.t_evector = numpy.array(self.t_evector)
        self.v_t = numpy.zeros([self.dim*2, self.dim*2]) # real
        for i in range(self.dim):
            j = 2*i
            evector = numpy.transpose(self.m_evector)[i]
            phi_i = numpy.angle(evector[j])
            exp_phi_i = numpy.exp(1j*phi_i)
            try:
                ratio = evector[j+1]/evector[j]
                beta_i = 1./numpy.imag(ratio)
                alpha_i = -beta_i * numpy.real(ratio)
            except FloatingPointError:
                beta_i = -1.
                alpha_i = 0.
            phase_i = numpy.angle(self.m_evalue[j])
            self.t_evector[j,   j] = cmath.sqrt(beta_i)*exp_phi_i
            self.t_evector[j+1, j] = 1./cmath.sqrt(beta_i)*(-alpha_i+1j)*exp_phi_i
            self.t_evector[j,   j+1] = numpy.conj(self.t_evector[j, j])
            self.t_evector[j+1, j+1] = numpy.conj(self.t_evector[j+1, j])
            self.phase[i] = phase_i
            sign = 1.
            if beta_i < 0:
                sign = -1.
            self.v_t[j, j] = sign*beta_i
            self.v_t[j, j+1] = -sign*alpha_i
            self.v_t[j+1, j] = -sign*alpha_i
            self.v_t[j+1, j+1] = sign*(1+alpha_i*alpha_i)/beta_i
        self.r = numpy.dot(self.m_evector, numpy.linalg.inv(self.t_evector))
        r_inv = numpy.linalg.inv(self.r)
        self.t = numpy.dot(r_inv, numpy.dot(self.m, self.r))

    def get_v_m(self, eigen_emittances):
        """
        Get the periodic ellipse to the transfer matrix equation
        M^T V_in M = V_out, such that V_out = V_in
        - eigen_emittances: list of length N (for a transfer matrix of size
          2Nx2N). Should be filled with floats. Each float gives the 
          eigenemittance in a particular direction.
        Returns a 2Nx2N matrix V such that M^T V M = V
        """
        if len(eigen_emittances) != self.dim:
            raise ValueError("Eigen emittances "+str(eigen_emittances)+\
                    "of wrong length (should be "+str(self.dim)+")")
        v_m = copy.deepcopy(self.v_t)
        for i in range(self.dim):
            v_m[i*2, i*2] *= eigen_emittances[i]
            v_m[i*2, i*2+1] *= eigen_emittances[i]
            v_m[i*2+1, i*2] *= eigen_emittances[i]
            v_m[i*2+1, i*2+1] *= eigen_emittances[i]
        v_m = numpy.dot(numpy.dot(self.r, v_m), numpy.transpose(self.r))
        return numpy.real(v_m)

    def get_phase_advance(self, axis):
        """
        Return the phase advance [rad] in the direction given by axis.
        - axis: integer, 0 >= axis < N for a transfer matrix of size 2Nx2N. 
          Defines the axis in the eigenspace along which the optics quantity is
          calculated.
        """
        return self.phase[axis]


    def get_beta(self, axis):
        """
        Return the optical beta in the direction given by axis.
        - axis: integer, 0 >= axis < N for a transfer matrix of size 2Nx2N. 
          Defines the axis in the eigenspace along which the optics quantity is
          calculated.
        """
        return self.v_t[2*axis, 2*axis]


    def get_alpha(self, axis):
        """
        Return the optical alpha in the direction given by axis.
        - axis: integer, 0 >= axis < N for a transfer matrix of size 2Nx2N. 
          Defines the axis in the eigenspace along which the optics quantity is
          calculated.
        """
        return -self.v_t[2*axis+1, 2*axis]

    def get_gamma(self, axis):
        """
        Return the optical gamma in the direction given by axis.
        - axis: integer, 0 >= axis < N for a transfer matrix of size 2Nx2N. 
          Defines the axis in the eigenspace along which the optics quantity is
          calculated.
        """
        return self.v_t[2*axis+1, 2*axis+1]

    def print_tests(self):
        print("M")
        print(self.m)
        print("M evector")
        print(self.m_evector)
        print("M evalue")
        print(self.m_evalue)
        for i in range(self.dim):
            j = 2*i
            cos_mu = (self.t[j, j]+self.t[j+1, j+1])/2.
            print("Cos", i, cos_mu, math.cos(self.phase[i]))
            j_matrix = numpy.array([
                [self.t[j, j]-cos_mu, self.t[j, j+1]],
                [self.t[j+1, j], self.t[j+1, j+1]-cos_mu]
            ])
            det_j = cmath.sqrt(numpy.linalg.det(j_matrix))
            j_matrix /= det_j
            print("Sin", i, det_j, math.sin(self.phase[i]))
            print("Beta", i, j_matrix[0, 1], self.v_t[j, j])
            print("Alpha", i, j_matrix[0, 0], -j_matrix[1, 1], -self.v_t[j, j+1])
            print("Gamma", i, -j_matrix[1, 0], self.v_t[j+1, j+1])
        print("T evector")
        print(self.t_evector)
        print("R")
        print(self.r)
        print("T")
        print(self.t)
        print()
        print("V_T", numpy.linalg.det(self.v_t))
        print(self.v_t)
        v_t_transported = numpy.dot(self.t, numpy.dot(self.v_t, numpy.transpose(self.t)))
        print("T^T V_T T", numpy.linalg.det(v_t_transported))
        print(v_t_transported)
        print("V_M")
        v_m = self.get_v_m(range(2, 2+self.dim))
        print(v_m)
        print("M^T V_M M")
        v_m_transported = numpy.dot(self.m, numpy.dot(v_m, numpy.transpose(self.m)))
        print(v_m_transported)

    det_tolerance = 1e-6



def _random_rotated(dim):
    unit = numpy.zeros([dim, dim])
    for i in range(dim):
        unit[i, i] = 1.
    test_matrix = numpy.array(unit)
    for i, angle in enumerate(numpy.random.uniform(0., 360., dim-1)):
        rot_matrix = numpy.array(unit)
        rot_matrix[0, 0] = math.cos(angle)
        rot_matrix[i+1, i+1] = math.cos(angle)
        rot_matrix[0, i+1] = math.sin(angle)
        rot_matrix[i+1, 0] = -math.sin(angle)
        test_matrix = numpy.dot(rot_matrix, test_matrix)
    for i, angle in enumerate(numpy.random.uniform(0., 360., dim-1)):
        rot_matrix = numpy.array(unit)
        rot_matrix[0, 0] = math.cos(angle)
        rot_matrix[i+1, i+1] = math.cos(angle)
        rot_matrix[0, i+1] = math.sin(angle)
        rot_matrix[i+1, 0] = -math.sin(angle)
        test_matrix = numpy.dot(numpy.transpose(rot_matrix), test_matrix)
    return test_matrix

def test_get_closed_ellipse():
    numpy.random.seed(1)
    print "============== 2D ============="
    test_matrix = [ # block-diagonal, r should be identity
    [0.75**0.5, 0.5],
    [-0.5, 0.75**0.5],
    ]
    DecoupledTransferMatrix(test_matrix).print_tests()
    print "\n\n============== Rotated 4D "+"="*100
    test_matrix = [
        [0.75**0.5, 0.5,  0.0, 1.0],
        [-0.5, 0.75**0.5, -1.0, 0.0],
        [0.0, -1.0,  0.75**0.5, 0.5,],
        [1.0, 0.0,  -0.5, 0.75**0.5]
    ]
    DecoupledTransferMatrix(test_matrix).print_tests()
    print "\n\n============== Rotated 6D "+"="*100
    test_matrix = _random_rotated(6)
    DecoupledTransferMatrix(test_matrix).print_tests()
    

if __name__ == "__main__":
    test_get_closed_ellipse()

