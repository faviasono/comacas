import pandas as pd
import json
import datetime as dt
import os


STATE_DF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/alloggiati/stati.csv")
STATE_DF = pd.read_csv(STATE_DF_PATH)


def read_reservations_booker(booking_excel_path: str, property: int, booker: str) -> dict:
    """
    Read the reservations from the excel file
    :param property: 1 for  'Com a cas', 2 for 'Com a cas #2'
    :param booker: name of the booker to search for in the DF
    :return: Dictionary with the reservations for the booker
    """

    if property not in [1, 2]:
        raise ValueError("Property must be 1 or 2")
    if booker is None:
        raise ValueError("Booker name must be provided")

    df: pd.DataFrame = pd.read_excel(booking_excel_path)
    df = df[~df["Property name"].str.contains("#2")] if property == 1 else df[df["Property name"].str.contains("#2")]
    df["Booker name"] = df["Booker name"].str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("utf-8")
    df = df[df["Booker name"] == booker]

    if df.empty:
        raise ValueError(f"Booker name {booker} not present")
    return json.loads(df.to_json(orient="records"))[0]


def format_list_json_to_txt(docs_completed_list: list[dict]):
    def _format_data_json_to_txt(entry: dict, index: int) -> str:
        """Format data as expected from Alloggiati Web - Police documentation"""
        index_str = "18" if index == 0 else "20"
        arrival_date = dt.datetime.strptime(entry["Arrival"], "%d %B %Y")
        departure_date = dt.datetime.strptime(entry["Departure"], "%d %B %Y")

        days_of_stay = (departure_date - arrival_date).days
        last_name = entry["last_name"].upper()
        first_name = entry["first_name"].upper()
        gender = "2" if entry["gender"] == "F" else "1"
        date_of_birth = dt.datetime.strptime(entry["date_of_birth"], "%d-%m-%Y")
        municipality = (
            f"{entry['municipality']}{' ' * (9 - len(entry['municipality']))}" if entry["country"] == "ITA" else " " * 9
        )
        province = entry["province"] if entry["country"] == "Italy" else " " * 2
        country = entry["country"]
        try:
            contry_code = STATE_DF[STATE_DF.Description == country.upper()].Code.values[0]
        except Exception:
            contry_code = "NONE"
        nationality = contry_code
        if index == 0:
            document_type = "PASOR" if entry["document_type"] == "Passport" else "IDENT"
            document_number = f"{entry['document_id']}{' ' * (20- len(entry['document_id']) )}"
            document_place = entry["municipality"] if entry["country"] == "Italy" else contry_code
        else:
            document_type = " " * 5
            document_number = " " * 20
            document_place = " " * 9

        # Formatting the data as per the provided instructions
        formatted_entry = (
            f"{index_str}{arrival_date.strftime('%d/%m/%Y')}{days_of_stay:02d}{last_name}{' ' * (50 - len(last_name))}"
            f"{first_name}{' ' * (30 - len(first_name))}{gender}{date_of_birth.strftime('%d/%m/%Y')}"
            f"{municipality}{province}{contry_code}{nationality}{document_type}{document_number}{document_place}\r\n"
        )
        return formatted_entry

    return "".join([_format_data_json_to_txt(doc, i) for i, doc in enumerate(docs_completed_list)])


def json2alloggiati(*, json_file: str, reservation_file: str, property: int, booker: str):
    """Given a document json file and the reservation file from Booking.com generate the file required for Alloggiati web"""
    booker: dict = read_reservations_booker(reservation_file, property, booker)
    docs_jsons = json.load(open(json_file))
    # add to all the docs within a reservation the reservation details
    [doc.update(booker) for doc in docs_jsons]
    formatted_docs = format_list_json_to_txt(docs_jsons)
    return formatted_docs
