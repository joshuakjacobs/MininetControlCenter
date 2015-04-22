cd;cd ryu/ryu/app/gui_topology;
sed -i "s/app_manager.require_app('ryu.app.ofctl_rest')/#app_manager.require_app('ryu.app.ofctl_rest')/g" gui_topology.py
