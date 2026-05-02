import argparse

import iamcli_common
import iamfunction


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    parser.add_argument('--user', action='append')
    args = parser.parse_args()

    def process_account(account, iam):
        users = args.user or iamcli_common.get_config_list(account, 'delete_users')

        if len(users) == 0:
            print('削除対象ユーザーなし')
            return

        for user_name in users:
            result = iamfunction.delete_user(user_name, iam)
            print(result['Note'])

    if not args.config and not args.user:
        print('入力エラー: configなしの場合、--user を指定してください')
        return

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
