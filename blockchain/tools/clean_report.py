import json
import sys


# a function for cleaning a report for analyzing particular contract
def main():
    # load the report
    with open(sys.argv[1], 'r') as infile:
        data = json.loads(infile.read())

    # get the coverage data
    coverage_data = data['coverage']

    # iterate over contracts
    contracts = coverage_data.keys()
    for contract in contracts:
        # iterate over the branches
        branches = coverage_data[contract]['branches'].copy()
        for branch in branches:
            # remove the key if the main contract is not in the branch
            if contract not in branch:
                del coverage_data[contract]['branches'][branch]

        # iterate over the statements
        statements = coverage_data[contract]['statements'].copy()
        for statement in statements:
            if contract not in statement:
                del coverage_data[contract]['statements'][statement]

    # reassign the whole data set
    data['coverage'] = coverage_data

    # rewrite teh file
    with open(sys.argv[1], 'w') as outfile:
        outfile.write(json.dumps(data, indent=4))


if __name__ == '__main__':
    main()
