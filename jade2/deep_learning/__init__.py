from jade2.basic import restype_definitions as resd

from .util import *
from .enums import *

aacodes = resd.RestypeDefinitions().get_all_one_letter_codes()


one_body_metrics_all =  ["fa_dun_dev_res_energy_2D",
                     "fa_dun_rot_res_energy_2D",
                     "fa_dun_semi_res_energy_2D",
                     "fa_sol_res_energy_2D",
                     "lk_ball_bridge_res_energy_2D",
                     "lk_ball_bridge_uncpl_res_energy_2D",
                     "lk_ball_iso_res_energy_2D",
                     "lk_ball_res_energy_2D",
                     "omega_res_energy_2D",
                     "rama_prepro_res_energy_2D",
                     "res_sasa_2D"]

one_body_metrics_sol = ["fa_sol_res_energy_2D"]