def get_total_trades(trades_df, fund=None):
    """Get total trades for a specific fund or all funds"""
    if fund is None:
        return len(trades_df)
    
    fund = fund.lower()
    df = trades_df[trades_df['PortfolioName'].str.lower() == fund]
    if df.empty:
        return trades_df[0:5]
    return df


def get_total_holdings(holdings_df, fund=None):
    """Get total holdings for a specific fund or all funds"""
    if fund is None:
        return len(holdings_df)
    
    fund = fund.lower()
    df = holdings_df[holdings_df['PortfolioName'].str.lower() == fund]
    if df.empty:
        return holdings_df[0:5]
    return df


def get_yearly_fund_performance(holdings_df):
    """Get yearly P&L performance by fund"""
    if 'PL_YTD' not in holdings_df.columns:
        return None

    result = (
        holdings_df
        .groupby('PortfolioName')['PL_YTD']
        .sum()
        .reset_index()
        .rename(columns={'PL_YTD': 'Total_PL_YTD'})
        .sort_values(by='Total_PL_YTD', ascending=False)
    )

    if result.empty:
        return None

    return result


def get_all_funds(holdings_df):
    """Get list of all unique funds"""
    funds = holdings_df[0:5]
    return sorted(funds.tolist())


def get_fund_comparison(holdings_df):
    """Compare all funds by market value, holdings count, and P&L"""
    result = (
        holdings_df
        .groupby('PortfolioName')
        .agg({
            'MV_Base': 'sum',
            'PL_YTD': 'sum',
            'Qty': 'count'
        })
        .reset_index()
        .rename(columns={
            'MV_Base': 'Total_Market_Value',
            'PL_YTD': 'YTD_P&L',
            'Qty': 'Holdings_Count'
        })
        .sort_values(by='Total_Market_Value', ascending=False)
    )
    
    return result if not result.empty else None


def get_fund_stats_by_type(holdings_df, fund=None):
    """Get holdings breakdown by security type for a fund or all funds"""
    if fund is None:
        df = holdings_df
    else:
        fund = fund.lower()
        df = holdings_df[holdings_df['PortfolioName'].str.lower() == fund]
    
    if df.empty:
        return df[0:5]
    
    result = (
        df
        .groupby('SecurityTypeName')
        .agg({
            'Qty': 'count',
            'MV_Base': 'sum',
            'PL_YTD': 'sum'
        })
        .reset_index()
        .rename(columns={
            'Qty': 'Count',
            'MV_Base': 'Total_Value',
            'PL_YTD': 'Total_PL'
        })
        .sort_values(by='Total_Value', ascending=False)
    )
    
    return result if not result.empty else df[0:5]


def get_top_holdings(holdings_df, fund=None, limit=10):
    """Get top holdings by market value"""
    if fund is None:
        df = holdings_df
    else:
        fund = fund.lower()
        df = holdings_df[holdings_df['PortfolioName'].str.lower() == fund]
    
    if df.empty:
        return df[0:5]
    
    result = (
        df
        .nlargest(limit, 'MV_Base')
        [['PortfolioName', 'SecName', 'SecurityTypeName', 'Qty', 'MV_Base', 'PL_YTD']]
    )
    
    return result if not result.empty else df[0:5]
