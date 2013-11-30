from world import World
import os, sys


def main(argv):
    if not argv:
        print "No input file supplied!"
        return
    cwd = os.getcwd()
    input_f = os.path.join(cwd, argv[0])
    if len(argv) > 1:
        output_f = os.path.join(cwd, argv[1])
        sys.stdout = open(output_f, 'w')

    world = World(input_f)
    world.start()


if __name__ == '__main__':
    net = main(sys.argv[1:])
