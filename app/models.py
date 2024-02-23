from app import db

class Dataset(db.Model):
    __tablename__ = 'dataset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    date_added = db.Column(db.DateTime)
    column_count = db.Column(db.Integer)
    columns = db.Column(db.Text)
    row_count = db.Column(db.Integer)
    data = db.Column(db.JSON)
    def __repr__(self):
        return ('<Dataset {}, column count {}, columns {} rows {}>'
                .format(self.name, self.column_count, self.columns, self.row_count))