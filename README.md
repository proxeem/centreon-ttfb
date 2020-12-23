# Time To First Byte plugin for Centreon

## Overview
This plugin allows you to monitor the TTFB of yours website with more details than the classic built-in plugin `HTTP Response Time`.

* DNS lookup duration
* TCP connection duration
* TLS handshake duration
* Backend duration (i.e. the time during your application is really working)
* Data download duration

## Installation
* Upload the script to the Centreon plugins directory (`/usr/lib/centreon/plugins/`).
* Create a new control command called `Protocol-TTFB-Response-Time` and configure it as below (the name of the command doesn't matter) :

``$CENTREONPLUGINS$/webperf/ttfb/ttfb-metrics.py --timeout='30' --http-backend='python' --proto='$_SERVICEPROTOCOL$' --hostname=$_SERVICEHOSTNAME$ --urlpath='$_SERVICEURLPATH$' --warning='$_SERVICEWARNING$' --critical='$_SERVICECRITICAL$' $_HOSTEXTRAOPTIONS$ $_SERVICEEXTRAOPTIONS$``

* Create a new service template called `Protocol-TTFB-Response-Time` and configure it as below :

    - set template to `generic-active-service-custom`
    - set control command to `Protocol-TTFB-Response-Time` (created on the previous step)
    - keep `PROTOCOL`, `HOSTNAME` and `EXTRAOPTIONS` to blank
    - set `URLPATH` to `/`
    - set `WARNING` and `CRITICAL` to your default values (200 and 600 are good 'Google' values)

* Then, create your TTFB measurement services !
