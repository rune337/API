import argparse

import iamcli_common
import iamfunction


def process_account(account, iam):
    users = iamfunction.list_all_users(iam)

    if len(users) == 0:
        print('ユーザーなし')
        return

    for user in users:
        print(user['UserName'])


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    args = parser.parse_args()

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
