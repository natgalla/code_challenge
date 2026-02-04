import requests

from app.extensions import db
from app.models import Starship, Manufacturer

SWAPI_BASE_URL = "https://www.swapi.tech/api/"


def fetch_starship_data():
    """Fetch all starships and manufacturers from SWAPI and store in DB.
    Prevents slow and repetitive calls to the API on a per user or per session basis.
    Ideally a job would periodically update this to make sure data remains 1:1 with SWAPI"""

    endpoint = SWAPI_BASE_URL + 'starships?expanded=true'

    try:
        # endpoint will eventually return null and break the loop
        while endpoint:
            r = requests.get(endpoint)
            if r.status_code == 200:
                r_json = r.json()
                for record in r_json.get('results', []):
                    # fetch all properties from expanded results
                    props = record.get('properties', {})
                    uid = record.get('uid')

                    if db.session.execute(db.select(Starship).filter_by(uid=uid)).scalar_one_or_none():
                        continue

                    # save properties to Starship model
                    starship = Starship(
                        uid=uid,
                        name=props.get('name'),
                        model=props.get('model'),
                        cost_in_credits=props.get('cost_in_credits'),
                        length=props.get('length'),
                        max_atmosphering_speed=props.get('max_atmosphering_speed'),
                        crew=props.get('crew'),
                        passengers=props.get('passengers'),
                        cargo_capacity=props.get('cargo_capacity'),
                        consumables=props.get('consumables'),
                        hyperdrive_rating=props.get('hyperdrive_rating'),
                        mglt=props.get('MGLT'),
                        starship_class=props.get('starship_class'),
                        url=props.get('url')
                    )

                    manufacturer_str = props.get('manufacturer', '')
                    # split by comma or slash
                    manufacturer_str = manufacturer_str.replace('/', ',')
                    for name in [m.strip() for m in manufacturer_str.split(',')]:
                        # skip garbage data
                        if not name or name.lower() in ['inc', 'inc.']:
                            continue
                        # fix typo
                        if name == 'Cyngus Spaceworks':
                            name = 'Cygnus Spaceworks'
                        manufacturer = db.session.execute(db.select(Manufacturer).filter_by(name=name)).scalar_one_or_none()
                        if not manufacturer:
                            manufacturer = Manufacturer(name=name)
                            db.session.add(manufacturer)
                        starship.manufacturers.append(manufacturer)
                    # save Starship to the db
                    db.session.add(starship)
                endpoint = r_json.get('next')
            else:
                break
        db.session.commit()
        starship_count = db.session.execute(db.select(db.func.count()).select_from(Starship)).scalar()
        manufacturer_count = db.session.execute(db.select(db.func.count()).select_from(Manufacturer)).scalar()
        print(f'Loaded {starship_count} starships and {manufacturer_count} manufacturers into DB')
    except Exception as e:
        # generic exception handling; with more testing should be made more explicit to catch specific errors
        print(f'An API error occurred: {e}')
