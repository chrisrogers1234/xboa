import xboa.common as common
from xboa.hit import BadEventError
from xboa.hit.factory import MausRootHitFactory
import unittest
import json
import ROOT
import libMausCpp

def _make_tracks(mc_event, n_tracks = 0, n_steps = 0):
    track_vector = ROOT.MAUS.TrackArray()
    for i in range(n_tracks):
        track = ROOT.MAUS.Track()
        track.SetParticleId(-13)
        track.SetTrackId(i+1)
        step_vector = ROOT.MAUS.StepArray()
        for j in range(n_steps):
            step = ROOT.MAUS.Step()
            step.SetPosition(ROOT.MAUS.ThreeVector(1., 2., 3.))
            step.SetMomentum(ROOT.MAUS.ThreeVector(4., 5., 6.))
            step.SetBField(ROOT.MAUS.ThreeVector(15., 16., 17.))
            step.SetEField(ROOT.MAUS.ThreeVector(18., 19., 20.))
            step.SetTime(10.)
            step.SetProperTime(12.)
            step.SetPathLength(14.)

            step_vector.push_back(step)
        track.SetSteps(step_vector)
        track_vector.push_back(track)
    mc_event.SetTracks(track_vector)

def _make_test_spill(n_spills, n_events, n_virts, n_tracks = 0, n_steps = 0):
    test_spill = ROOT.MAUS.Spill()
    mc_events = ROOT.MAUS.Spill.MCEventPArray()
    for i in range(n_events):
        an_mc_event = ROOT.MAUS.MCEvent()
        primary = ROOT.MAUS.Primary()
        primary.SetPosition(ROOT.MAUS.ThreeVector(1., 2., 3.))
        primary.SetMomentum(ROOT.MAUS.ThreeVector(0.5, 0.5, 1./2.**0.5))
        primary.SetTime(7.)
        primary.SetEnergy(200.)
        primary.SetRandomSeed(9)
        primary.SetParticleId(-13)
        if i == 2:
            primary.SetParticleId(int(1e9))
        an_mc_event.SetPrimary(primary)
        virtuals = ROOT.MAUS.VirtualHitArray()
        for j in range(n_virts):
            virtual = ROOT.MAUS.VirtualHit()
            virtual.SetPosition(ROOT.MAUS.ThreeVector(1., 2., 3.))
            virtual.SetMomentum(ROOT.MAUS.ThreeVector(4., 5., 6.))
            virtual.SetBField(ROOT.MAUS.ThreeVector(15., 16., 17.))
            virtual.SetEField(ROOT.MAUS.ThreeVector(18., 19., 20.))
            virtual.SetParticleId(-13)
            virtual.SetStationId(j)
            virtual.SetTrackId(9)
            virtual.SetTime(10.)
            virtual.SetMass(common.pdg_pid_to_mass[13])
            virtual.SetCharge(11.)
            virtual.SetProperTime(12.)
            virtual.SetPathLength(14.)
            if j == 1:
                virtual.SetParticleId(int(1e9))
            virtuals.push_back(virtual)
        _make_tracks(an_mc_event, n_tracks, n_steps)
        an_mc_event.SetVirtualHits(virtuals)
        mc_events.push_back(an_mc_event)
    test_spill.SetMCEvents(mc_events)
    data = ROOT.MAUS.Data()
    test_tree = ROOT.TTree("Spill", "TTree")
    test_tree.Branch("data", data, data.GetSizeOf(), 1)
    data.SetSpill(test_spill)
    for i in range(n_spills):
        test_spill.SetSpillNumber(99)
        test_tree.Fill()
    return test_tree

class TestMausRootHitFactory(unittest.TestCase):
    def test_init_document(self):
        fac = MausRootHitFactory(_make_test_spill(0, 0, 0), "maus_root_primary")
        try:
            fac = MausRootHitFactory(_make_test_spill(0, 0, 0), "no_type")
            self.assertTrue(False)
        except KeyError:
            pass

    def test_primary(self):
        fac = MausRootHitFactory(_make_test_spill(2, 3, 0), "maus_root_primary")
        p = (200.**2.-common.pdg_pid_to_mass[13]**2)**0.5
        for i in range(6):
            test = {'x':1., 'y':2., 'z':3., 'p':p, 't':7.,
                     'energy':200., 'pid':-13, 'spill':99}
            hit = fac.make_hit()
            if i == 2 or i == 5:
                test['pid'] = int(1e9)
                test['p'] = test['energy']
            for key, value in test.iteritems():
                self.assertAlmostEqual(hit[key], value)
        try:
            hit = fac.make_hit()
            self.assertTrue(False)
        except BadEventError:
            pass

    def test_virtual_hit(self):
        fac = MausRootHitFactory(_make_test_spill(2, 3, 2),
                                 "maus_root_virtual_hit")
        mass = common.pdg_pid_to_mass[13]
        energy = (4.**2+5.**2.+6.**2+mass**2)**0.5
        test = {'x':1., 'y':2., 'z':3., 'px':4., 'py':5., 'pz':6., 'station':8, 
                't':10., 'pid':-13, 'mass':mass, 
                'energy':energy, 'bx':15., 'by':16., 'bz':17.,
                'ex':18., 'ey':19., 'ez':20., 'proper_time':12.,
                'path_length':14., 'spill':99}
        for spill_index in range(2):
            for i in range(6):
                hit = fac.make_hit()
                test['station'] = i % 2
                test['event_number'] = i/2
                if i % 2 == 1:
                    test['pid'] = int(1e9)
                else:
                    test['pid'] = -13
                for key, value in test.iteritems():
                    self.assertAlmostEqual(hit[key], value,
                        msg="Failed "+str(key)+" "+str(hit[key])+" "+str(value))
        try:
            hit = fac.make_hit()
            self.assertTrue(False)
        except BadEventError:
            pass


    def test_step(self):
        spill = _make_test_spill(2, 3, 0, 3, 4)
        fac = MausRootHitFactory(spill, "maus_root_step")
        mass = common.pdg_pid_to_mass[13]
        energy = (4.**2+5.**2.+6.**2+mass**2)**0.5
        test = {'x':1., 'y':2., 'z':3., 'px':4., 'py':5., 'pz':6.,
                'particle_number':9, 't':10., 'pid':-13, 'mass':mass, 
                'energy':energy, 'bx':15., 'by':16., 'bz':17.,
                'ex':18., 'ey':19., 'ez':20., 'proper_time':12., 'pid':-13,
                'path_length':14., 'spill':99}
        for spill_index in range(2):
            for i in range(36):
                hit = fac.make_hit()
                test['station'] = i%4
                test['event_number'] = i/12 # 3 tracks * 4 steps
                test['particle_number'] = (i%12)/4+1
                for key, value in test.iteritems():
                    self.assertAlmostEqual(hit[key], value,
                        msg="Failed "+str(key)+" ev: "+str(i)+\
                            " test: "+str(hit[key])+" ref: "+str(value))
        try:
            hit = fac.make_hit()
            self.assertTrue(False)
        except BadEventError:
            pass


    def test_scifi_trackpoint(self):
        raise NotImplementedError("Need a test here")

    def test_test_function(self):
        raise NotImplementedError("Need a test here")

if __name__ == "__main__":
    unittest.main()

