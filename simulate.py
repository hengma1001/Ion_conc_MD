import simtk.openmm as mm
import simtk.openmm.app as app
import simtk.unit as u

print 'Create water system...'
pdb = app.PDBFile('6A.pdb')
forcefield = app.ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
modeller = app.Modeller(pdb.topology, pdb.positions)

print 'Add water and 0.15 M KCL...'
modeller.deleteWater()
#modeller.addHydrogens(forcefield)
modeller.addSolvent(forcefield, ionicStrength=0.15*u.molar, positiveIon='K+')
app.PDBFile.writeFile(modeller.topology, modeller.positions, open('6A_waterion.pdb', 'w'))

print 'Create the simulation system...'
system = forcefield.createSystem(modeller.topology, nonbondedMethod=app.PME, nonbondedCutoff=1.0*u.nanometer)

print 'Create and add external force...'
#force = mm.CustomExternalForce('100*step(z-7)')
force = mm.CustomExternalForce('-max(0,z-29.5)*100')
system.addForce(force)

for chain in modeller.topology._chains:
    for residue in chain._residues: 
        for atom in residue._atoms: 
            #print atom.name, atom.index, atom.residue
            if atom.name == 'K' or atom.name == 'Cl': 
                force.addParticle(atom.index, [])

print 'build simulation...'
integrator = mm.LangevinIntegrator(300*u.kelvin, 1/u.picosecond, 0.002*u.picoseconds)
platform = mm.Platform.getPlatformByName('CUDA')
properties = {'DeviceIndex': '2',  'CudaPrecision': 'mixed'}
simulation = app.Simulation(modeller.topology, system, integrator, platform, properties)
simulation.context.setPositions(modeller.positions)

print 'minimizing energy...'
simulation.minimizeEnergy()

print 'set up reporters...'
simulation.reporters.append(app.DCDReporter('output.dcd', 5000))
simulation.reporters.append(app.StateDataReporter('output.log', 5000, step=True, time=True, potentialEnergy=True, temperature=True, speed=True))
simulation.reporters.append(app.CheckpointReporter('checkpnt.chk', 5000))

print 'run simulation for 100 ns ...'
simulation.step(50000000)


