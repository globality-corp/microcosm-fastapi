# uvicorn test_project.test_run:app --reload


from fastapi import FastAPI

app = FastAPI()


async def read_item(*args, **kwargs):
    #print(kwargs, args)
    # We can in fact modify these args
    # https://github.com/Kwpolska/merge_args/blob/master/merge_args.py
    # https://chriswarrick.com/blog/2018/09/20/python-hackery-merging-signatures-of-two-python-functions/
    return {"item_id": item_id}

def add_to_graph():
    read_item.__annotations__ = {
        "item_id": float,
        **read_item.__annotations__
    }

    has_dest_ret = 'return' in dest.__annotations__
    if has_dest_ret:
        dest_ret = dest.__annotations__['return']

    app.get("/items/{item_id}")(read_item)


add_to_graph()