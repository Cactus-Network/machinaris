#
# CLI interactions with the plotman script.
#

from app.models.plotman import PID_FILE
import datetime
import os
import psutil
import signal
import shutil
import time
import traceback
import yaml

from flask import Flask, jsonify, abort, request, flash
from subprocess import Popen, TimeoutExpired, PIPE
from app.models import plotman
from app import app

PLOTMAN_SCRIPT = '/chia-blockchain/venv/bin/plotman'

RELOAD_MINIMUM_SECS = 30 # Don't query plotman unless at least this long since last time.

last_plotting_summary = None 
last_plotting_summary_load_time = None 

def load_plotting_summary():
    global last_plotting_summary
    global last_plotting_summary_load_time
    if last_plotting_summary and last_plotting_summary_load_time >= \
            (datetime.datetime.now() - datetime.timedelta(seconds=RELOAD_MINIMUM_SECS)):
        return last_plotting_summary

    proc = Popen("{0} {1} < /dev/tty".format(PLOTMAN_SCRIPT,'status'), stdout=PIPE, stderr=PIPE, shell=True)
    try:
        outs, errs = proc.communicate(timeout=30)
    except TimeoutExpired:
        proc.kill()
        proc.communicate()
        abort(500, description="The timeout is expired!")
    if errs:
        app.logger.error(errs.decode('utf-8'))
        abort(500, description=errs.decode('utf-8'))
    
    cli_stdout = outs.decode('utf-8')
    #app.logger.info("Here is: {0}".format(cli_stdout))
    last_plotting_summary = plotman.PlottingSummary(cli_stdout.splitlines(), get_plotman_pid())
    last_plotting_summary_load_time = datetime.datetime.now()
    return last_plotting_summary

def start_plotman():
    global last_plotting_summary
    app.logger.info("Starting Plotman run....")
    try:
        logfile = "/root/.chia/plotman/logs/plotman.log"
        log_fd = os.open(logfile, os.O_RDWR|os.O_CREAT)
        log_fo = os.fdopen(log_fd, "w+")
        proc = Popen("{0} {1} </dev/tty".format(PLOTMAN_SCRIPT,'plot'), \
            shell=True, universal_newlines=True, stdout=log_fo, stderr=log_fo)
    except:
        app.logger.info(traceback.format_exc())
        flash('Failed to start Plotman plotting run!', 'danger')
        flash('Please see: {0}'.format(logfile), 'warning')
    else:
        last_plotting_summary = None # Force a refresh on next load
        flash('Plotman started successfully.', 'success')
        time.sleep(5) # Wait for Plotman to start a plot running for display in table

def action_plots(form):
    global last_plotting_summary
    app.logger.info("Actioning plots....")
    action = form.get('action')
    plot_ids = form.getlist('plot_id')
    app.logger.info("About to {0} plots: {1}".format(action, plot_ids))
    for plot_id in plot_ids:
        try:
            logfile = "/root/.chia/plotman/logs/plotman.log"
            log_fd = os.open(logfile, os.O_RDWR|os.O_CREAT)
            log_fo = os.fdopen(log_fd, "w+")
            proc = Popen("{0} {1} {2}</dev/tty".format(PLOTMAN_SCRIPT, action, plot_id), \
                shell=True, universal_newlines=True, stdout=log_fo, stderr=log_fo)
        except:
            app.logger.info(traceback.format_exc())
            flash('Failed to {0} selected plot {1}.'.format(action, plot_id), 'danger')
            flash('Please see: {0}'.format(logfile), 'warning')
            return
    last_plotting_summary = None # Force a refresh on next load
    flash('Plotman was able to {0} the selected plots successfully.'.format(action), 'success')
    time.sleep(5) # Wait for Plotman to complete its actions

def get_plotman_pid():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'plotman' and 'plot' in proc.info['cmdline']:
            return proc.info['pid']
    return None

def stop_plotman():
    global last_plotting_summary
    app.logger.info("Stopping Plotman run....")
    try:
        os.kill(get_plotman_pid(), signal.SIGTERM)
    except:
        app.logger.info(traceback.format_exc())
        flash('Failed to stop Plotman plotting run!', 'danger')
        flash('Please see /root/.chia/plotman/logs/plotman.log', 'warning')
    else:
        last_plotting_summary = None # Force a refresh on next load
        flash('Plotman stopped successfully.  No new plots will be started, but existing ones will continue on.', 'success')

def save_config(config):
    try:
        # Validate the YAML first
        yaml.safe_load(config)
        # Save a copy of the old config file
        src="/root/.chia/plotman/plotman.yaml"
        dst="/root/.chia/plotman/plotman."+time.strftime("%Y%m%d-%H%M%S")+".yaml"
        shutil.copy(src,dst)
        # Now save the new contents to main config file
        with open(src, 'w') as writer:
            writer.write(config)
    except Exception as ex:
        app.logger.info(traceback.format_exc())
        flash('Updated plotman.yaml failed validation! Fix and save or refresh page.', 'danger')
        flash(str(ex), 'warning')
    else:
        flash('Nice! plotman.yaml validated and saved successfully.', 'success')
        flash('NOTE: Currently requires restarting plotman to pickup changes via Docker exec or Container restart.', 'info')
