dic_val = clickData2.values()
        cur_lat = float(clickData2['points'][0]['lat'])
        cur_lon = float(clickData2['points'][0]['lon'])
        resp = request.urlopen(
            'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1'.format(
                lat=cur_lat, lon=cur_lon))
        req_json = json.loads((resp.peek().decode('utf-8')))
        add_string = ""
        add_string += req_json['address']['road'] + '\n'
        add_string += req_json['address']['town'] + '\n'
        add_string += req_json['address']['city'] + '\n'
        add_string += req_json['address']['state_district'] + '\n'
        print(add_string)
        print(req_json.peek())
        return add_string, go.Figure(), go.Figure()