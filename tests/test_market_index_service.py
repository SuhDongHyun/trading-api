import unittest
from unittest.mock import Mock

from stock.domain.market import OverseasMarketIndexPrice
from stock.service.market_index_service import MarketIndexService


def make_service():
    domestic = Mock()
    overseas = Mock()
    stock_list = Mock()
    vkospi = Mock()
    vix = Mock()
    fear_greed = Mock()
    service = MarketIndexService(
        domestic, overseas, stock_list, vkospi, vix, fear_greed
    )
    return service, domestic, overseas, stock_list, vkospi, vix, fear_greed


class MarketIndexServiceTest(unittest.TestCase):
    """시장 지표 서비스의 역할별 포트 연결과 코드 매핑을 검증한다."""

    def test_service_maps_treasury_code_and_queries_overseas_market_port(self):
        service, _, overseas, _, _, _, _ = make_service()
        expected = [
            OverseasMarketIndexPrice(
                date="20260105",
                open_price=3.1,
                high_price=3.2,
                low_price=3.0,
                close_price=3.15,
            )
        ]
        overseas.get_overseas_market_index_prices.return_value = expected

        result = service.get_korea_3y_treasury_yield("20260105", "20260107")

        overseas.get_overseas_market_index_prices.assert_called_once_with(
            "I", "Y0101", "20260105", "20260107"
        )
        self.assertEqual(result, expected)

    def test_service_maps_sp500_code_and_queries_overseas_market_port(self):
        service, _, overseas, _, _, _, _ = make_service()

        service.get_sp500_index("20260105", "20260107")

        overseas.get_overseas_market_index_prices.assert_called_once_with(
            "N", "SPX", "20260105", "20260107"
        )

    def test_service_maps_kospi_code_and_queries_domestic_market_port(self):
        service, domestic, _, _, _, _, _ = make_service()

        service.get_kospi_index("20260105", "20260107")

        domestic.get_domestic_market_index_prices.assert_called_once_with(
            "U", "0001", "20260105", "20260107"
        )

    def test_source_specific_indexes_use_their_own_ports(self):
        service, _, _, _, vkospi, vix, fear_greed = make_service()

        service.get_vkospi_index("20260105", "20260107")
        service.get_vix_index("20260105", "20260107")
        service.get_fear_and_greed_index()

        vkospi.get_vkospi_index.assert_called_once_with("20260105", "20260107")
        vix.get_vix_index.assert_called_once_with("20260105", "20260107")
        fear_greed.get_fear_and_greed_index.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
