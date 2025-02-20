from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def get_object(cls, session, **kwargs):
        return session.query(cls).filter_by(**kwargs).first()

    @classmethod
    def get_all_object(cls, session, **filters):
        try:
            query = session.query(cls)
            if filters:
                query = query.filter_by(**filters)
            return query.all()
        except Exception as e:
            raise Exception(
                f'Erreur lors de la récupération: {str(e)}')

    @classmethod
    def _save_object(cls, session, obj):
        try:
            session.add(obj)
            session.commit()
            return obj
        except Exception as e:
            session.rollback()
            raise Exception(
                f"Erreur lors de la création "
                f"de l'objet {cls.__name__}: {str(e)}"
            )

    @classmethod
    def _delete_object(cls, session, obj):
        try:
            session.delete(obj)
            session.commit()
            return obj
        except Exception as e:
            session.rollback()
            raise Exception(
                f"Erreur lors de la suppression "
                f"de l'objet {cls.__name__}: {str(e)}"
            )
