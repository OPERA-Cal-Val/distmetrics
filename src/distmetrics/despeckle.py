import numpy as np
from multiprocess import Pool
from skimage.restoration import denoise_tv_bregman
from tqdm import tqdm


def despeckle_one_rtc_arr_with_tv(X: np.ndarray, reg_param: float = 5, noise_floor_db: float = -22) -> np.ndarray:
    X_c = np.clip(X, 1e-7, 1)
    X_db = 10 * np.log10(X_c, out=np.full(X_c.shape, np.nan), where=(~np.isnan(X_c)))
    X_db[np.isnan(X_c)] = noise_floor_db - 1
    weight = 1.0 / reg_param
    X_db_dspkl = denoise_tv_bregman(X_db, weight=weight, isotropic=True, eps=1e-3)
    X_dspkl = np.power(10, X_db_dspkl / 10.0)
    X_dspkl[np.isnan(X)] = np.nan
    X_dspkl = np.clip(X_dspkl, 0, 1)
    return X_dspkl


def despeckle_rtc_arrs_with_tv(
    arrs: list[np.ndarray], reg_param=5, noise_floor_db: float = -22, n_jobs: int = 10
) -> list[np.ndarray]:
    def dspkl(X: np.ndarray):
        return despeckle_one_rtc_arr_with_tv(X, reg_param=reg_param, noise_floor_db=noise_floor_db)

    with Pool(n_jobs) as pool:
        arrs_dspk = pool.map(dspkl, tqdm(arrs, desc='Despeckling RTC'))
    return arrs_dspk
