# trading_assistant/risk_management.py

from .utils import get_logger

logger = get_logger(__name__)

def calculate_position_size(total_capital: float, risk_percentage: float, stop_loss_price: float, entry_price: float) -> float:
    """
    Calculates the suggested number of shares to trade based on capital, risk, and stop-loss.
    """
    if not isinstance(total_capital, (int, float)) or total_capital <= 0:
        logger.error("Total capital must be a positive number.")
        return 0
    if not isinstance(risk_percentage, (int, float)) or not 0 < risk_percentage <= 1:
        logger.error("Risk percentage must be between 0 and 1.")
        return 0
    if not isinstance(stop_loss_price, (int, float)) or stop_loss_price <= 0:
        logger.error("Stop-loss price must be a positive number.")
        return 0
    if not isinstance(entry_price, (int, float)) or entry_price <= 0:
        logger.error("Entry price must be a positive number.")
        return 0
    if (entry_price > stop_loss_price and entry_price - stop_loss_price <= 0) or \
       (entry_price < stop_loss_price and stop_loss_price - entry_price <= 0):
        logger.error("Stop-loss price is at or above/below the entry price.")
        return 0

    risk_amount = total_capital * risk_percentage
    risk_per_share = abs(entry_price - stop_loss_price)

    if risk_per_share > 0:
        suggested_shares = risk_amount / risk_per_share
        return suggested_shares
    else:
        logger.error("Risk per share is zero.")
        return 0

def calculate_stop_loss(entry_price: float, risk_tolerance: float, is_long: bool = True) -> float:
    """
    Calculates the suggested stop-loss price.
    """
    if not isinstance(entry_price, (int, float)) or entry_price <= 0:
        logger.error("Entry price must be a positive number.")
        return 0
    if not isinstance(risk_tolerance, (int, float)) or risk_tolerance < 0:
        logger.error("Risk tolerance must be a non-negative number.")
        return 0

    try:
        if is_long:
            if 0 < risk_tolerance < 1:
                 stop_loss = entry_price * (1 - risk_tolerance)
            else:
                 stop_loss = entry_price - risk_tolerance
        else:
            if 0 < risk_tolerance < 1:
                 stop_loss = entry_price * (1 + risk_tolerance)
            else:
                 stop_loss = entry_price + risk_tolerance
        return stop_loss
    except Exception as e:
        logger.error(f"Error calculating stop-loss: {e}")
        return 0

def calculate_target_profit(entry_price: float, target_profit_factor: float, is_long: bool = True) -> float:
    """
    Calculates the suggested target profit price.
    """
    if not isinstance(entry_price, (int, float)) or entry_price <= 0:
        logger.error("Entry price must be a positive number.")
        return 0
    if not isinstance(target_profit_factor, (int, float)) or target_profit_factor <= 0:
        logger.error("Target profit factor must be a positive number.")
        return 0

    try:
        if is_long:
            target_profit = entry_price * (1 + target_profit_factor)
        else:
            target_profit = entry_price * (1 - target_profit_factor)
        return target_profit
    except Exception as e:
        logger.error(f"Error calculating target profit: {e}")
        return 0
