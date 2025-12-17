db = db.getSiblingDB("orion-bodik");

db.entities.createIndex(
  { "_id.servicePath": 1, "_id.id": 1 },
  { name: "sp_id_compound" }
);

db.entities.createIndex(
  { "attrNames": 1 },
  { name: "attrNames_1" }
);

db.entities.createIndex(
  { "creDate": 1 },
  { name: "creDate_1" }
);
