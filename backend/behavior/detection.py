# Pattern detection algorithms (Design Doc Section 14)
# Placeholder for revenge_trading, overtrading, loss_chasing detection logic


def detect_revenge_trading(trades):
    """Detect revenge trading pattern: many trades in short time after loss."""
    if not trades or len(trades) < 3:
        return False
    # TODO: implement using trade timestamps and pnl
    return False


def detect_overtrading(trades, avg_daily_trades=8):
    """Detect overtrading: trades count >> average."""
    if not trades:
        return False
    return len(trades) > avg_daily_trades * 2


def detect_loss_chasing(trades):
    """Detect loss chasing: consecutive losses with increasing size."""
    if not trades or len(trades) < 2:
        return False
    # TODO: implement
    return False
