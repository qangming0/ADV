def syncResponse(res, syn_devids):
    hasResponse = set(res.devResState['offlines'])
    hasResponse.update(res.devResState['success'])
    hasResponse.update(res.devResState['failed'])

    notResponse = syn_devids.exclude(
        dss_device__dev_ident__in=list(hasResponse)
    ).values_list('dss_device__dev_ident', flat=True).distinct()
    res.devResState['failed'] = res.devResState['failed'] + list(notResponse)
    if len(res.devResState['offlines']) > 0 and len(res.devResState['failed']) > 0:
        res.success = False
    return res