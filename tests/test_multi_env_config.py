def test_sandbox_and_prod_have_distinct_bases(sandbox_cfg, prod_cfg):
    assert sandbox_cfg.base_url != prod_cfg.base_url
    assert sandbox_cfg.api_client_key != prod_cfg.api_client_key
