import argparse

import iamcli_common
import iamfunction


def process_account(account, iam):
    groups = iamfunction.list_all_groups(iam)

    if len(groups) == 0:
        print('グループなし')
        return

    for group in groups:
        print(group['GroupName'])


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    args = parser.parse_args()

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
