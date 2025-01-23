from .factories import CelestialFactory, SpaceportFactory


class Stars:
    
    @classmethod
    def create_sol(cls, context=None):
        if context is None:
            context = object()
        
        celestials = [CelestialFactory(name="Sol", celestial_type=1, size=100)]
        context.sun = sun = celestials[0]
        
        context.planets = planets = [
                    CelestialFactory(name='Mercur', celestial_type=2, orbits=sun, size=2.4), #0
                    CelestialFactory(name='Venus',  celestial_type=2, orbits=sun, size=6),
                    CelestialFactory(name='Terra',  celestial_type=2, orbits=sun, size=6.4), #2
                    CelestialFactory(name='Mars',   celestial_type=2, orbits=sun, size=3.4),
                    CelestialFactory(name='Jupiter',celestial_type=2, orbits=sun, size=69.9), #4
                    CelestialFactory(name='Saturn', celestial_type=2, orbits=sun, size=58.2),
                    CelestialFactory(name='Uranus', celestial_type=2, orbits=sun, size=25.4), #6
                    CelestialFactory(name='Neptune',celestial_type=2, orbits=sun, size=24.6),
                    CelestialFactory(name='Pluto',celestial_type=3,   orbits=sun, size=1.1), #8
                   ]
        celestials.extend(planets)
        
        context.moons = moons = [
                   CelestialFactory(name='Luna', celestial_type=3, orbits=planets[2], size=1.7), #0
                   CelestialFactory(name='Phobos', celestial_type=4, orbits=planets[3], size=0.006),
                   CelestialFactory(name='Deimos', celestial_type=4, orbits=planets[3], size=0.011), #2
                   CelestialFactory(name='Io', celestial_type=3, orbits=planets[4], size=1.8),
                   CelestialFactory(name='Europa', celestial_type=3, orbits=planets[4], size=1.5), #4
                   CelestialFactory(name='Ganymede', celestial_type=3, orbits=planets[4], size=2.6),
                   CelestialFactory(name='Callisto', celestial_type=3, orbits=planets[4], size=2.4), #6
                   #...
                   CelestialFactory(name='Charon', celestial_type=4, orbits=planets[8], size=0.6)
                ]
        celestials.extend(moons)
        context.celestials = celestials
        
        # create space ports
        context.spaceports = [
            SpaceportFactory(celestial=planets[2], name="Houston IPS", ),
            SpaceportFactory(celestial=moons[0], name='Copernicus'),
            SpaceportFactory(celestial=planets[3], name='Utopia Planitia'),
            SpaceportFactory(celestial=moons[2], name='Ares Station'),
        ]
