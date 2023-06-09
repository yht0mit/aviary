
import pytest

import aviary.metrics.utils as utils



def test_horizontal_distance():

    lat1 = 51.507389
    lon1 = 0.127806

    lat2 = 50.6083
    lon2 = -1.9608

    result = utils.horizontal_distance_m(lon1, lat1, lon2, lat2)
    assert result == pytest.approx(1000 * 176.92, 0.01)

    result_nm = utils.horizontal_distance_nm(lon1, lat1, lon2, lat2)
    assert result_nm == pytest.approx(round(result/utils._ONE_NM))
