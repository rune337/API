import argparse

import iamcli_common
import iamfunction


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    parser.add_argument('--group')
    parser.add_argument('--policy-arn')
    parser.add_argument('--policy-name')
    args = parser.parse_args()

    def process_account(account, iam):
        if args.group and (args.policy_arn or args.policy_name):
            targets = [{'group': args.group, 'policy_name': args.policy_name}]
        else:
            targets = iamcli_common.get_config_list(account, 'attach_group_policies')

        if len(targets) == 0:
            print('グループに追加するポリシーなし')
            return

        for target in targets:
            try:
                policy_arn = iamcli_common.get_policy_arn(
                    account,
                    cli_policy_arn=args.policy_arn,
                    policy_name=target.get('policy_name') or target.get('policy'),
                    config_value=target,
                )
            except ValueError as e:
                print('入力エラー: ' + str(e))
                return

            result = iamfunction.attach_group_policy(target['group'], policy_arn, iam)
            print(result['Note'])

    if not args.config and not (args.group and args.policy_arn):
        print('入力エラー: configなしの場合、--group と --policy-arn を指定してください')
        return

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
