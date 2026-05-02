import argparse

import iamcli_common
import iamfunction


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    parser.add_argument('--group', action='append')
    args = parser.parse_args()

    def process_account(account, iam):
        groups = args.group or iamcli_common.get_config_list(account, 'delete_groups')

        if len(groups) == 0:
            print('削除対象グループなし')
            return

        for group_name in groups:
            result = iamfunction.delete_group(group_name, iam)
            print(result['Note'])

    if not args.config and not args.group:
        print('入力エラー: configなしの場合、--group を指定してください')
        return

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
