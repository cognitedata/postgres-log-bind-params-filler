import unittest
import bind_params_filler


class TestBinder(unittest.TestCase):

    def test_params_string_to_param_pairs(self):
        params1 = """2021-12-21 17:00:32.071 UTC-61c20813.14e28-DETAIL:  parameters: $1 = '9'"""
        pairs1 = bind_params_filler.params_string_to_pairs(params1)
        self.assertEqual(len(pairs1), 1)
        self.assertEqual(pairs1[0], ('$1', "'9'"))

        params2 = """2021-12-21 17:00:32.071 UTC-61c20813.14e28-DETAIL:  parameters: $1 = '9', $2 = '2665986911814221'"""
        pairs2 = bind_params_filler.params_string_to_pairs(params2)
        self.assertEqual(len(pairs2), 2)
        self.assertEqual(pairs2[0], ('$1', "'9'"))
        self.assertEqual(pairs2[1], ('$2', "'2665986911814221'"))

        params3 = """2021-12-21 15:38:57.172 UTC-61c1f4f7.a8cc-DETAIL:  parameters: $1 = '5', $2 = '1758350297916640', $3 = '8744815131059416', $4 = '2021-09-07 07:41:29.737226', $5 = '2021-09-07 07:42:29.239094', $6 = '1001', $7 = '5', $8 = '1758350297916640', $9 = '8744815131059416', $10 = 'iw29_120070630', $11 = '2021-09-07 07:41:29.737226', $12 = '2021-09-07 07:42:29.239094', $13 = '1001', $14 = '1001'"""
        pairs3 = bind_params_filler.params_string_to_pairs(params3)
        self.assertEqual(len(pairs3), 14)
        self.assertEqual(pairs3[13], ('$14', "'1001'"))

    def test_replace_params_line_into_sql(self):
        params_line = """2021-12-21 17:00:32.071 UTC-61c20813.14e28-DETAIL:  parameters: $1 = '9', $11 = '0'"""
        sql_in = """select $11 = $1"""
        sql_out = """select '0' = '9'"""

        sql = bind_params_filler.replace_params_line_into_sql(sql_in, params_line)
        self.assertEqual(sql, sql_out)


if __name__ == "__main__":
    unittest.main()
