import argparse

import iamcli_common
import iamfunction


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    parser.add_argument('--scope', default='Local')
    args = parser.parse_args()

    def process_account(account, iam):
        policies = iamfunction.list_all_policies(iam, args.scope)

        if len(policies) == 0:
            print('ポリシーなし')
            return

        for policy in policies:
            print(policy['PolicyName'] + ' ' + policy['Arn'])

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
