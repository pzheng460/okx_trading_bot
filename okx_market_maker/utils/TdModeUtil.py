from okx_market_maker.utils.OkxEnum import AccountConfigMode, InstType, TdMode
from okx_market_maker.config.settings import TRADING_MODE

class TdModeUtil:
    @classmethod
    def decide_trading_mode(cls, 
                            account_config: AccountConfigMode, 
                            inst_type: InstType,
                            td_mode_setting: str = TRADING_MODE
    ) -> TdMode:
        """
        交易模式：在下单时，需要指定交易模式。

        非杠杆账户（Non-margined）：
        - 现货交易（SPOT）和期权买方（OPTION buyer）：cash（现货模式）
        单币种杠杆账户（Single-currency margin account）：
        - 逐仓杠杆（Isolated MARGIN）：isolated（逐仓模式）
        - 全仓杠杆（Cross MARGIN）：cross（全仓模式）
        - 全仓现货（Cross SPOT）：cash（现货模式）
        - 全仓合约/永续/期权（Cross FUTURES/SWAP/OPTION）：cross（全仓模式）
        - 逐仓合约/永续/期权（Isolated FUTURES/SWAP/OPTION）：isolated（逐仓模式）
        多币种杠杆账户（Multi-currency margin account）：
        - 逐仓杠杆（Isolated MARGIN）：isolated（逐仓模式）
        - 全仓现货（Cross SPOT）：cross（全仓模式）
        - 全仓合约/永续/期权（Cross FUTURES/SWAP/OPTION）：cross（全仓模式）
        - 逐仓合约/永续/期权（Isolated FUTURES/SWAP/OPTION）：isolated（逐仓模式）
        组合保证金账户（Portfolio margin）：
        - 逐仓杠杆（Isolated MARGIN）：isolated（逐仓模式）
        - 全仓现货（Cross SPOT）：cross（全仓模式）
        - 全仓合约/永续/期权（Cross FUTURES/SWAP/OPTION）：cross（全仓模式）
        - 逐仓合约/永续/期权（Isolated FUTURES/SWAP/OPTION）：isolated（逐仓模式）

        Args:   
            account_config: AccountConfigMode
            inst_type: InstType
            td_mode_setting: TdMode

        Returns:
            TdMode: The trade mode to be used when placing an order.
        """

        # 检查现货模式
        if account_config == AccountConfigMode.CASH:
            if inst_type not in [InstType.SPOT, InstType.OPTION]:
                raise ValueError(f"Invalid inst type {inst_type} in Cash Mode!")
            return TdMode.CASH
        
        # 检查单币种杠杆模式
        if account_config == AccountConfigMode.SINGLE_CCY_MARGIN:
            if td_mode_setting in TdMode:
                assigned_trading_mode = TdMode(td_mode_setting)
                if inst_type not in [InstType.SPOT, InstType.MARGIN] and assigned_trading_mode == TdMode.CASH:
                    return TdMode.CROSS
                if inst_type == InstType.SPOT:
                    return TdMode.CASH
                return assigned_trading_mode
            if inst_type == InstType.SPOT:
                return TdMode.CASH
            return TdMode.CROSS
        
        # 检查多币种杠杆模式
        if account_config in [AccountConfigMode.MULTI_CCY_MARGIN, AccountConfigMode.PORTFOLIO_MARGIN]:
            if td_mode_setting in TdMode:
                assigned_trading_mode = TdMode(td_mode_setting)
                if assigned_trading_mode == TdMode.CASH:
                    return TdMode.CROSS
                if inst_type == InstType.MARGIN:
                    return TdMode.ISOLATED
                if inst_type == InstType.SPOT:
                    return TdMode.CROSS
                return assigned_trading_mode
            if inst_type == InstType.MARGIN:
                return TdMode.ISOLATED
            return TdMode.CROSS
        
        # 无效的账户配置模式
        raise ValueError(f"Invalid Account config mode {account_config}!")
