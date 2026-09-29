from views.team import TeamView

class MockEvent:
    def __init__(self, data):
        class MockControl:
            def __init__(self, d):
                self.data = d
        self.control = MockControl(data)

def test_click():
    tv = TeamView()
    tv.load_data()
    # Find the ID of the first equipped pokemon
    first_pk = tv.team_row.controls[0]
    
    # first_pk is the outer container
    stack = first_pk.content
    inner_container = stack.controls[0]
    pk_id = inner_container.data
    
    print(f"Trying to open details for pk_id: {pk_id}")
    e = MockEvent(pk_id)
    try:
        tv.open_details(e)
        print("Success! details_modal is open.")
    except Exception as ex:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_click()
